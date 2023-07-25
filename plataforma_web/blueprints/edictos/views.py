"""
Edictos, vistas
"""
import datetime
import json
from pathlib import Path
from urllib.parse import quote

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.exceptions import MyAnyError
from lib.google_cloud_storage import get_blob_name_from_url, get_media_type_from_filename, get_file_from_gcs
from lib.safe_string import safe_expediente, safe_message, safe_numero_publicacion, safe_string
from lib.time_to_text import dia_mes_ano, mes_en_palabra
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.edictos.forms import EdictoEditForm, EdictoNewForm, EdictoSearchForm, EdictoSearchAdminForm
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

edictos = Blueprint("edictos", __name__, template_folder="templates")

MODULO = "EDICTOS"
LIMITE_DIAS = 365
LIMITE_ADMINISTRADORES_DIAS = 365  # Administradores pueden manipular un anio


@edictos.route("/edictos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    edicto = Edicto.query.get_or_404(Edicto.decode_id(id_hashed))
    dia, mes, anio = dia_mes_ano(edicto.creado)
    return render_template("edictos/print.jinja2", edicto=edicto, dia=dia, mes=mes.upper(), anio=anio)


@edictos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@edictos.route("/edictos")
def list_active():
    """Listado de Edictos activos"""
    # Si es administrador ve todo
    if current_user.can_admin("EDICTOS"):
        return render_template(
            "edictos/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos los Edictos",
            estatus="A",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "edictos/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Edictos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
        )
    # Ninguno de los anteriores
    return redirect(url_for("edictos.list_distritos"))


@edictos.route("/edictos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Edictos inactivos"""
    # Si es administrador ve todo
    if current_user.can_admin("EDICTOS"):
        return render_template(
            "edictos/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todos los Edictos inactivos",
            estatus="B",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "edictos/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Edictos inactivos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
        )
    # Ninguno de los anteriores
    return redirect(url_for("edictos.list_distritos"))


@edictos.route("/edictos/distritos")
def list_distritos():
    """Listado de Distritos"""
    return render_template(
        "edictos/list_distritos.jinja2",
        distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
    )


@edictos.route("/edictos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template(
        "edictos/list_autoridades.jinja2",
        distrito=distrito,
        autoridades=Autoridad.query.filter_by(distrito=distrito).filter_by(es_jurisdiccional=True).filter_by(estatus="A").order_by(Autoridad.clave).all(),
    )


@edictos.route("/edictos/autoridad/<int:autoridad_id>")
def list_autoridad_edictos(autoridad_id):
    """Listado de Edictos activos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("EDICTOS"):
        plantilla = "edictos/list_admin.jinja2"
    else:
        plantilla = "edictos/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Edictos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
    )


@edictos.route("/edictos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_autoridad_edictos_inactive(autoridad_id):
    """Listado de Edictos inactivos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("EDICTOS"):
        plantilla = "edictos/list_admin.jinja2"
    else:
        plantilla = "edictos/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Edictos inactivos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
    )


@edictos.route("/edictos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Edictos"""
    if current_user.can_admin("EDICTOS"):
        puede_elegir_autoridad = True
    elif current_user.autoridad.es_jurisdiccional:
        puede_elegir_autoridad = False
    else:
        puede_elegir_autoridad = True
    if puede_elegir_autoridad:
        form_search = EdictoSearchAdminForm()
    else:
        form_search = EdictoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        fallo_validacion = False
        # Autoridad es un campo obligatorio
        if puede_elegir_autoridad:
            autoridad = Autoridad.query.get(form_search.autoridad.data)
            plantilla = "edictos/list_admin.jinja2"
        else:
            autoridad = current_user.autoridad
            plantilla = "edictos/list.jinja2"
        busqueda["autoridad_id"] = autoridad.id
        titulos.append(autoridad.distrito.nombre_corto + ", " + autoridad.descripcion_corta)
        # Fecha
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("hasta " + busqueda["fecha_hasta"])
        # Descripción
        if form_search.descripcion.data:
            busqueda["descripcion"] = safe_string(form_search.descripcion.data)
            titulos.append("descripción " + busqueda["descripcion"])
        # Expediente
        try:
            expediente = safe_expediente(form_search.expediente.data)
            if expediente != "":
                busqueda["expediente"] = expediente
                titulos.append("expediente " + expediente)
        except (IndexError, ValueError):
            flash("Expediente incorrecto.", "warning")
            fallo_validacion = True
        # Número de publicación
        try:
            numero_publicacion = safe_numero_publicacion(form_search.numero_publicacion.data)
            if numero_publicacion != "":
                busqueda["numero_publicacion"] = numero_publicacion
                titulos.append("numero_publicacion " + numero_publicacion)
        except (IndexError, ValueError):
            flash("Número de Publicación incorrecto.", "warning")
            fallo_validacion = True
        # Mostrar resultados
        if not fallo_validacion:
            return render_template(
                plantilla,
                filtros=json.dumps(busqueda),
                titulo="Edictos con " + ", ".join(titulos),
            )
    # Mostrar buscador donde puede elegir la autoridad
    if puede_elegir_autoridad:
        return render_template(
            "edictos/search_admin.jinja2",
            form=form_search,
            distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
            autoridades=Autoridad.query.filter_by(es_jurisdiccional=True).filter_by(estatus="A").order_by(Autoridad.clave).all(),
        )
    # Mostrar buscador con la autoridad fija
    form_search.distrito.data = current_user.autoridad.distrito.nombre
    form_search.autoridad.data = current_user.autoridad.descripcion
    return render_template("edictos/search.jinja2", form=form_search)


@edictos.route("/edictos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de edictos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Edicto.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Edicto.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Edicto.fecha <= request.form["fecha_hasta"])
    if "descripcion" in request.form:
        consulta = consulta.filter(Edicto.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))
    if "expediente" in request.form:
        try:
            expediente = safe_expediente(request.form["expediente"])
            consulta = consulta.filter_by(expediente=expediente)
        except (IndexError, ValueError):
            pass
    if "numero_publicacion" in request.form:
        try:
            numero_publicacion = safe_numero_publicacion(request.form["numero_publicacion"])
            consulta = consulta.filter_by(numero_publicacion=numero_publicacion)
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(Edicto.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for edicto in registros:
        data.append(
            {
                "fecha": edicto.fecha.strftime("%Y-%m-%d 00:00:00"),
                "detalle": {
                    "descripcion": edicto.descripcion,
                    "url": url_for("edictos.detail", edicto_id=edicto.id),
                },
                "expediente": edicto.expediente,
                "numero_publicacion": edicto.numero_publicacion,
                "archivo": {
                    "descargar_url": f"/edictos/descargar?url={quote(edicto.url)}",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@edictos.route("/edictos/datatable_json_admin", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def datatable_json_admin():
    """DataTable JSON para listado de edictos administradores"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Edicto.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Edicto.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Edicto.fecha <= request.form["fecha_hasta"])
    if "descripcion" in request.form:
        consulta = consulta.filter(Edicto.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))
    if "expediente" in request.form:
        try:
            expediente = safe_expediente(request.form["expediente"])
            consulta = consulta.filter_by(expediente=expediente)
        except (IndexError, ValueError):
            pass
    if "numero_publicacion" in request.form:
        try:
            numero_publicacion = safe_numero_publicacion(request.form["numero_publicacion"])
            consulta = consulta.filter_by(numero_publicacion=numero_publicacion)
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(Edicto.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for edicto in registros:
        data.append(
            {
                "creado": edicto.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": edicto.autoridad.clave,
                "fecha": edicto.fecha.strftime("%Y-%m-%d 00:00:00"),
                "detalle": {
                    "descripcion": edicto.descripcion,
                    "url": url_for("edictos.detail", edicto_id=edicto.id),
                },
                "expediente": edicto.expediente,
                "numero_publicacion": edicto.numero_publicacion,
                "archivo": {
                    "descargar_url": f"/edictos/descargar?url={quote(edicto.url)}",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@edictos.route("/edictos/descargar", methods=["GET"])
def download():
    """Descargar archivo desde Google Cloud Storage"""
    url = request.args.get("url")
    try:
        # Obtener nombre del blob
        blob_name = get_blob_name_from_url(url)
        # Obtener tipo de media
        media_type = get_media_type_from_filename(blob_name)
        # Obtener archivo
        archivo = get_file_from_gcs(current_app.config["CLOUD_STORAGE_DEPOSITO_EDICTOS"], blob_name)
    except MyAnyError as error:
        flash(str(error), "warning")
        return redirect(url_for("edictos.list_active"))
    # Entregar archivo
    return current_app.response_class(archivo, mimetype=media_type)


@edictos.route("/edictos/refrescar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def refresh(autoridad_id):
    """Refrescar Edictos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("edictos.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="edictos.tasks.refrescar",
            descripcion=f"Refrescar edictos de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("edictos.list_autoridad_edictos", autoridad_id=autoridad.id))


@edictos.route("/edictos/<int:edicto_id>")
def detail(edicto_id):
    """Detalle de un Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    return render_template("edictos/detail.jinja2", edicto=edicto)


def new_success(edicto):
    """Mensaje de éxito en nuevo edicto"""
    piezas = ["Nuevo edicto"]
    if edicto.expediente != "":
        piezas.append(f"expediente {edicto.expediente},")
    if edicto.numero_publicacion != "":
        piezas.append(f"número {edicto.numero_publicacion},")
    piezas.append(f"fecha {edicto.fecha.strftime('%Y-%m-%d')} de {edicto.autoridad.clave}")
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(" ".join(piezas)),
        url=url_for("edictos.detail", edicto_id=edicto.id),
    )
    bitacora.save()
    return bitacora


@edictos.route("/edictos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Subir Edicto como juzgado"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("edictos.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("edictos.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("edictos.list_active"))
    if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("edictos.list_active"))

    # Si viene el formulario
    form = EdictoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("edictos/new.jinja2", form=form)

        # Validar descripcion
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Validar número de publicación
        try:
            numero_publicacion = safe_numero_publicacion(form.numero_publicacion.data)
        except (IndexError, ValueError):
            flash("El número de publicación es incorrecto.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Insertar registro
        edicto = Edicto(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            expediente=expediente,
            numero_publicacion=numero_publicacion,
        )
        edicto.save()

        # Elaborar nombre del archivo
        fecha_str = fecha.strftime("%Y-%m-%d")
        elementos = [fecha_str]
        if expediente != "":
            elementos.append(expediente.replace("/", "-"))
        if numero_publicacion != "":
            elementos.append(numero_publicacion.replace("/", "-"))
        elementos.append(safe_string(descripcion, max_len=64).replace(" ", "-"))
        elementos.append(edicto.encode_id())
        archivo_str = "-".join(elementos) + ".pdf"

        # Elaborar ruta Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        ruta_str = str(Path(autoridad.directorio_edictos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO_EDICTOS"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        edicto.archivo = archivo_str
        edicto.url = url
        edicto.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(edicto)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("edictos/new.jinja2", form=form)


@edictos.route("/edictos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def new_for_autoridad(autoridad_id):
    """Subir Edicto para una autoridad dada"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("edictos.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = EdictoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar descripcion
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Validar número de publicación
        try:
            numero_publicacion = safe_numero_publicacion(form.numero_publicacion.data)
        except (IndexError, ValueError):
            flash("El número de publicación es incorrecto.", "warning")
            return render_template("edictos/new.jinja2", form=form)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        edicto = Edicto(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            expediente=expediente,
            numero_publicacion=numero_publicacion,
        )
        edicto.save()

        # Elaborar nombre del archivo
        fecha_str = fecha.strftime("%Y-%m-%d")
        elementos = [fecha_str]
        if expediente != "":
            elementos.append(expediente.replace("/", "-"))
        if numero_publicacion != "":
            elementos.append(numero_publicacion.replace("/", "-"))
        elementos.append(safe_string(descripcion, max_len=64).replace(" ", "-"))
        elementos.append(edicto.encode_id())
        archivo_str = "-".join(elementos) + ".pdf"

        # Elaborar ruta Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        ruta_str = str(Path(autoridad.directorio_edictos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO_EDICTOS"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        edicto.archivo = archivo_str
        edicto.url = url
        edicto.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(edicto)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


def edit_success(edicto):
    """Mensaje de éxito al editar un edicto"""
    piezas = ["Editado edicto"]
    if edicto.expediente != "":
        piezas.append(f"expediente {edicto.expediente},")
    if edicto.numero_publicacion != "":
        piezas.append(f"número {edicto.numero_publicacion},")
    piezas.append(f"fecha {edicto.fecha.strftime('%Y-%m-%d')} de {edicto.autoridad.clave}")
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(" ".join(piezas)),
        url=url_for("edictos.detail", edicto_id=edicto.id),
    )
    bitacora.save()
    return bitacora


@edictos.route("/edictos/edicion/<int:edicto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(edicto_id):
    """Editar Edicto"""

    # Validar edicto
    edicto = Edicto.query.get_or_404(edicto_id)
    if not (current_user.can_admin("EDICTOS") or current_user.autoridad_id == edicto.autoridad_id):
        flash("No tiene permiso para editar este edicto.", "warning")
        return redirect(url_for("edictos.list_active"))

    form = EdictoEditForm()
    if form.validate_on_submit():
        es_valido = True
        edicto.fecha = form.fecha.data

        # Validar descripción
        edicto.descripcion = safe_string(form.descripcion.data)
        if edicto.descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            es_valido = False

        # Validar expediente
        try:
            edicto.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False

        # Validar número de publicación
        try:
            edicto.numero_publicacion = safe_numero_publicacion(form.numero_publicacion.data)
        except (IndexError, ValueError):
            flash("El número de publicación es incorrecto.", "warning")
            es_valido = False

        if es_valido:
            edicto.save()
            bitacora = edit_success(edicto)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    form.fecha.data = edicto.fecha
    form.descripcion.data = edicto.descripcion
    form.expediente.data = edicto.expediente
    form.numero_publicacion.data = edicto.numero_publicacion
    return render_template("edictos/edit.jinja2", form=form, edicto=edicto)


def delete_success(edicto):
    """Mensaje de éxito al eliminar un edicto"""
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Eliminado edicto de {edicto.autoridad.clave}"),
        url=url_for("edictos.detail", edicto_id=edicto.id),
    )
    bitacora.save()
    return bitacora


@edictos.route("/edictos/eliminar/<int:edicto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(edicto_id):
    """Eliminar Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("EDICTOS"):
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
            if limite_dt.timestamp() <= edicto.creado.timestamp():
                edicto.delete()
                bitacora = delete_success(edicto)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == edicto.autoridad_id:
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)
            if limite_dt.timestamp() <= edicto.creado.timestamp():
                edicto.delete()
                bitacora = delete_success(edicto)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))


def recover_success(edicto):
    """Mensaje de éxito al recuperar un edicto"""
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Recuperado edicto de {edicto.autoridad.clave}"),
        url=url_for("edictos.detail", edicto_id=edicto.id),
    )
    bitacora.save()
    return bitacora


@edictos.route("/edictos/recuperar/<int:edicto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(edicto_id):
    """Recuperar Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("EDICTOS"):
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
            if limite_dt.timestamp() <= edicto.creado.timestamp():
                edicto.recover()
                bitacora = recover_success(edicto)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == edicto.autoridad_id:
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)
            if limite_dt.timestamp() <= edicto.creado.timestamp():
                edicto.recover()
                bitacora = recover_success(edicto)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))
