"""
Glosas, vistas
"""
import datetime
import json
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.safe_string import safe_expediente, safe_message, safe_string
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.glosas.forms import GlosaEditForm, GlosaNewForm, GlosaSearchForm, GlosaSearchAdminForm
from plataforma_web.blueprints.glosas.models import Glosa

glosas = Blueprint("glosas", __name__, template_folder="templates")

MODULO = "GLOSAS"
SUBDIRECTORIO = "Glosas"
ORGANOS_JURISDICCIONALES = ["PLENO O SALA DEL TSJ", "TRIBUNAL DE CONCILIACION Y ARBITRAJE"]
LIMITE_DIAS = 365
LIMITE_ADMINISTRADORES_DIAS = 365


@glosas.route("/glosas/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    glosa = Glosa.query.get_or_404(Glosa.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(glosa.creado)
    return render_template("glosas/checkout.jinja2", glosa=glosa, dia=dia, mes=mes.upper(), ano=ano)


@glosas.before_request
@login_required
@permission_required(Permiso.VER_SEGUNDAS)
def before_request():
    """Permiso por defecto"""


@glosas.route("/glosas")
def list_active():
    """Listado de Glosas activos"""
    # Si es administrador ve todo
    if current_user.can_admin("glosas"):
        return render_template(
            "glosas/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos las Glosas",
            estatus="A",
        )
    # Si puede editar o crear glosas ve lo de su autoridad
    if current_user.can_edit("glosas") or current_user.can_insert("glosas"):
        autoridad = current_user.autoridad
        return render_template(
            "glosas/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Glosas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
        )
    # Ninguno de los anteriores
    return render_template(
        "glosas/list.jinja2",
        autoridad=None,
        filtros=json.dumps({"estatus": "A"}),
        titulo="Todos las Glosas",
        estatus="A",
    )


@glosas.route("/glosas/inactivos")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def list_inactive():
    """Listado de Glosas inactivas"""
    # Si es administrador ve todo
    if current_user.can_admin("glosas"):
        return render_template(
            "glosas/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todos las Glosas inactivas",
            estatus="B",
        )
    # Si puede editar o crear glosas ve lo de su autoridad
    if current_user.can_edit("glosas") or current_user.can_insert("glosas"):
        autoridad = current_user.autoridad
        return render_template(
            "glosas/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Glosas inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
        )
    # Ninguno de los anteriores
    return render_template(
        "glosas/list.jinja2",
        autoridad=None,
        filtros=json.dumps({"estatus": "B"}),
        titulo="Todos las Glosas inactivas",
        estatus="B",
    )


@glosas.route("/glosas/autoridades")
def list_autoridades():
    """Listado de Autoridades"""
    autoridades = Autoridad.query.filter(Autoridad.organo_jurisdiccional.in_(ORGANOS_JURISDICCIONALES)).filter_by(estatus="A").order_by(Autoridad.clave).all()
    return render_template("glosas/list_autoridades.jinja2", autoridades=autoridades)


@glosas.route("/glosas/autoridad/<int:autoridad_id>")
def list_autoridad_glosas(autoridad_id):
    """Listado de Glosas activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("glosas"):
        plantilla = "glosas/list_admin.jinja2"
    else:
        plantilla = "glosas/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Glosas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
    )


@glosas.route("/glosas/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def list_autoridad_glosas_inactive(autoridad_id):
    """Listado de Glosas inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("glosas"):
        plantilla = "glosas/list_admin.jinja2"
    else:
        plantilla = "glosas/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Glosas inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
    )


@glosas.route("/glosas/buscar", methods=["GET", "POST"])
def search():
    """Buscar Glosas"""
    if current_user.can_admin("glosas"):
        puede_elegir_autoridad = True
    elif current_user.can_edit("glosas") or current_user.can_insert("glosas"):
        puede_elegir_autoridad = False
    else:
        puede_elegir_autoridad = True
    if puede_elegir_autoridad:
        form_search = GlosaSearchAdminForm()
    else:
        form_search = GlosaSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        fallo_validacion = False
        # Autoridad es un campo obligatorio
        if puede_elegir_autoridad:
            autoridad = Autoridad.query.get(form_search.autoridad.data)
            plantilla = "glosas/list_admin.jinja2"
        else:
            autoridad = current_user.autoridad
            plantilla = "glosas/list.jinja2"
        busqueda["autoridad_id"] = autoridad.id
        titulos.append(autoridad.distrito.nombre_corto + ", " + autoridad.descripcion_corta)
        # Fecha
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("hasta " + busqueda["fecha_hasta"])
        # Tipo de juicio
        if form_search.tipo_juicio.data:
            busqueda["tipo_juicio"] = safe_string(form_search.tipo_juicio.data)
            titulos.append("tipo de juicio " + busqueda["tipo_juicio"])
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
        # Mostrar resultados
        if not fallo_validacion:
            return render_template(
                plantilla,
                filtros=json.dumps(busqueda),
                titulo="Glosas con " + ", ".join(titulos),
            )
    # Mostrar buscador donde puede elegir la autoridad
    if puede_elegir_autoridad:
        return render_template(
            "glosas/search_admin.jinja2",
            form=form_search,
            distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
            autoridades=Autoridad.query.filter(Autoridad.organo_jurisdiccional.in_(ORGANOS_JURISDICCIONALES)).filter_by(estatus="A").order_by(Autoridad.clave).all(),
        )
    # Mostrar buscador con la autoridad fija
    form_search.distrito.data = current_user.autoridad.distrito.nombre
    form_search.autoridad.data = current_user.autoridad.descripcion
    return render_template("glosas/search.jinja2", form=form_search)


@glosas.route("/glosas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de glosas"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    consulta = Glosa.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Glosa.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Glosa.fecha <= request.form["fecha_hasta"])
    if "tipo_juicio" in request.form:
        consulta = consulta.filter_by(tipo_juicio=request.form["tipo_juicio"])
    if "descripcion" in request.form:
        consulta = consulta.filter(Glosa.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))
    if "expediente" in request.form:
        try:
            consulta = consulta.filter_by(expediente=safe_expediente(request.form["expediente"]))
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(Glosa.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for glosa in registros:
        data.append(
            {
                "fecha": glosa.fecha.strftime("%Y-%m-%d"),
                "detalle": {
                    "descripcion": glosa.descripcion,
                    "url": url_for("glosas.detail", glosa_id=glosa.id),
                },
                "expediente": glosa.expediente,
                "tipo_juicio": glosa.tipo_juicio,
                "archivo": {
                    "url": glosa.url,
                },
            }
        )

    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@glosas.route("/glosas/datatable_json_admin", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_NOTARIALES)
def datatable_json_admin():
    """DataTable JSON para listado de glosas admin"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    consulta = Glosa.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Glosa.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Glosa.fecha <= request.form["fecha_hasta"])
    if "tipo_juicio" in request.form:
        consulta = consulta.filter_by(tipo_juicio=request.form["tipo_juicio"])
    if "descripcion" in request.form:
        consulta = consulta.filter(Glosa.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))
    if "expediente" in request.form:
        try:
            consulta = consulta.filter_by(expediente=safe_expediente(request.form["expediente"]))
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(Glosa.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for glosa in registros:
        data.append(
            {
                "creado": glosa.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": glosa.autoridad.clave,
                "fecha": glosa.fecha.strftime("%Y-%m-%d"),
                "detalle": {
                    "descripcion": glosa.descripcion,
                    "url": url_for("glosas.detail", glosa_id=glosa.id),
                },
                "expediente": glosa.expediente,
                "tipo_juicio": glosa.tipo_juicio,
                "archivo": {
                    "url": glosa.url,
                },
            }
        )

    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@glosas.route("/glosas/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def refresh(autoridad_id):
    """Refrescar Glosas"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("glosas.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="glosas.tasks.refrescar",
            descripcion=f"Refrescar glosas de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("glosas.list_autoridad_glosas", autoridad_id=autoridad.id))


@glosas.route("/glosas/<int:glosa_id>")
def detail(glosa_id):
    """Detalle de una Lista de Acuerdos"""
    glosa = Glosa.query.get_or_404(glosa_id)
    return render_template("glosas/detail.jinja2", glosa=glosa)


def new_success(glosa):
    """Mensaje de éxito en nueva glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Nueva glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_SEGUNDAS)
def new():
    """Subir Glosa como juzgado"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("glosas.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("glosas.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("glosas.list_active"))
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        flash("El juzgado/autoridad no tiene directorio para glosas.", "warning")
        return redirect(url_for("glosas.list_active"))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("glosas/new.jinja2", form=form)

        # Tomar tipo de juicio
        tipo_juicio = form.tipo_juicio.data

        # Validar descripcion
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Insertar registro
        glosa = Glosa(
            autoridad=autoridad,
            fecha=fecha,
            tipo_juicio=tipo_juicio,
            descripcion=descripcion,
            expediente=expediente,
        )
        glosa.save()

        # Elaborar nombre del archivo
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{descripcion_str}-{glosa.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_glosas, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        glosa.archivo = archivo_str
        glosa.url = url
        glosa.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(glosa)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new.jinja2", form=form)


@glosas.route("/glosas/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def new_for_autoridad(autoridad_id):
    """Subir Glosa para una autoridad dada"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("glosas.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        flash("El juzgado/autoridad no tiene directorio para glosas.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Tomar tipo de juicio
        tipo_juicio = form.tipo_juicio.data

        # Validar descripcion, porque safe_string puede resultar vacío
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        glosa = Glosa(
            autoridad=autoridad,
            fecha=fecha,
            tipo_juicio=tipo_juicio,
            descripcion=descripcion,
            expediente=form.expediente.data,
        )
        glosa.save()

        # Elaborar nombre del archivo
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{descripcion_str}-{glosa.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_glosas, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        glosa.archivo = archivo_str
        glosa.url = url
        glosa.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(glosa)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


def edit_success(glosa):
    """Mensaje de éxito al editar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Editada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/edicion/<int:glosa_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def edit(glosa_id):
    """Editar Glosa"""

    # Validar glosa
    glosa = Glosa.query.get_or_404(glosa_id)
    if not (current_user.can_admin("glosas") or current_user.autoridad_id == glosa.autoridad_id):
        flash("No tiene permiso para editar esta glosa.", "warning")
        return redirect(url_for("glosas.list_active"))

    form = GlosaEditForm()
    if form.validate_on_submit():
        es_valido = True
        glosa.fecha = form.fecha.data
        glosa.tipo_juicio = form.tipo_juicio.data
        glosa.descripcion = safe_string(form.descripcion.data)
        try:
            glosa.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False
        if es_valido:
            glosa.save()
            bitacora = edit_success(glosa)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.fecha.data = glosa.fecha
    form.tipo_juicio.data = glosa.tipo_juicio
    form.descripcion.data = glosa.descripcion
    form.expediente.data = glosa.expediente
    return render_template("glosas/edit.jinja2", form=form, glosa=glosa)


def delete_success(glosa):
    """Mensaje de éxito al eliminar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Eliminada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/eliminar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def delete(glosa_id):
    """Eliminar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("glosas"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= glosa.creado:
                glosa.delete()
                bitacora = delete_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == glosa.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= glosa.creado:
                glosa.delete()
                bitacora = delete_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))


def recover_success(glosa):
    """Mensaje de éxito al recuperar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Recuperada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/recuperar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def recover(glosa_id):
    """Recuperar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("glosas"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= glosa.creado:
                glosa.recover()
                bitacora = recover_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == glosa.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= glosa.creado:
                glosa.recover()
                bitacora = recover_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))
