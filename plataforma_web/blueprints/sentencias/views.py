"""
Sentencias, vistas
"""
import datetime
import json
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.safe_string import safe_expediente, safe_message, safe_sentencia, safe_string
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio
from plataforma_web.blueprints.sentencias.forms import SentenciaNewForm, SentenciaEditForm, SentenciaSearchForm, SentenciaSearchAdminForm
from plataforma_web.blueprints.sentencias.models import Sentencia

sentencias = Blueprint("sentencias", __name__, template_folder="templates")

MODULO = "SENTENCIAS"
SUBDIRECTORIO = "Sentencias"
LIMITE_DIAS = 1460
LIMITE_ADMINISTRADORES_DIAS = 1460


@sentencias.route("/sentencias/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    sentencia = Sentencia.query.get_or_404(Sentencia.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(sentencia.creado)
    return render_template("sentencias/checkout.jinja2", sentencia=sentencia, dia=dia, mes=mes.upper(), ano=ano)


@sentencias.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@sentencias.route("/sentencias")
def list_active():
    """Listado de Sentencias activas más recientes"""
    # Si es administrador ve todo
    if current_user.can_admin("sentencias"):
        return render_template(
            "sentencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Sentencias",
            estatus="A",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "sentencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Sentencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
        )
    # Ninguno de los anteriores
    return redirect(url_for("sentencias.list_distritos"))


@sentencias.route("/sentencias/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Sentencias inactivas"""
    # Si es administrador ve todo
    if current_user.can_admin("sentencias"):
        return render_template(
            "sentencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todas las Sentencias inactivas",
            estatus="B",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "sentencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Sentencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
        )
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("sentencias.list_distritos"))


@sentencias.route("/sentencias/distritos")
def list_distritos():
    """Listado de Distritos"""
    return render_template(
        "sentencias/list_distritos.jinja2",
        distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
    )


@sentencias.route("/sentencias/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template(
        "sentencias/list_autoridades.jinja2",
        distrito=distrito,
        autoridades=Autoridad.query.filter(Autoridad.distrito == distrito).filter_by(es_jurisdiccional=True).filter_by(es_notaria=False).filter_by(estatus="A").order_by(Autoridad.clave).all(),
    )


@sentencias.route("/sentencias/autoridad/<int:autoridad_id>")
def list_autoridad_sentencias(autoridad_id):
    """Listado de Sentencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("sentencias"):
        plantilla = "sentencias/list_admin.jinja2"
    else:
        plantilla = "sentencias/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Sentencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
    )


@sentencias.route("/sentencias/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_sentencias_inactive(autoridad_id):
    """Listado de Sentencias inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("sentencias"):
        plantilla = "sentencias/list_admin.jinja2"
    else:
        plantilla = "sentencias/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Sentencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
    )


@sentencias.route("/sentencias/buscar", methods=["GET", "POST"])
def search():
    """Buscar Sentencias"""
    if current_user.can_admin("sentencias"):
        puede_elegir_autoridad = True
    elif current_user.autoridad.es_jurisdiccional:
        puede_elegir_autoridad = False
    else:
        puede_elegir_autoridad = True
    if puede_elegir_autoridad:
        form_search = SentenciaSearchAdminForm()
    else:
        form_search = SentenciaSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        fallo_validacion = False
        # Autoridad es un campo obligatorio
        if puede_elegir_autoridad:
            autoridad = Autoridad.query.get(form_search.autoridad.data)
            plantilla = "sentencias/list_admin.jinja2"
        else:
            autoridad = current_user.autoridad
            plantilla = "sentencias/list.jinja2"
        busqueda["autoridad_id"] = autoridad.id
        titulos.append(autoridad.distrito.nombre_corto + ", " + autoridad.descripcion_corta)
        # Sentencia
        try:
            sentencia = safe_sentencia(form_search.sentencia.data)
            if sentencia != "":
                busqueda["sentencia"] = sentencia
                titulos.append("sentencia " + sentencia)
        except (IndexError, ValueError):
            flash("Sentencia incorrecta.", "warning")
            fallo_validacion = True
        # Expediente
        try:
            expediente = safe_expediente(form_search.expediente.data)
            if expediente != "":
                busqueda["expediente"] = expediente
                titulos.append("expediente " + expediente)
        except (IndexError, ValueError):
            flash("Expediente incorrecto.", "warning")
            fallo_validacion = True
        # Es paridad de genero
        # Fecha de publicacion
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("hasta " + busqueda["fecha_hasta"])
        # Mostrar resultados
        if not fallo_validacion:
            return render_template(
                plantilla,
                filtros=json.dumps(busqueda),
                titulo="Sentencias con " + ", ".join(titulos),
            )
    # Mostrar buscador donde puede elegir la autoridad
    if puede_elegir_autoridad:
        return render_template(
            "sentencias/search_admin.jinja2",
            form=form_search,
            distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
            autoridades=Autoridad.query.filter_by(es_jurisdiccional=True).filter_by(es_notaria=False).filter_by(estatus="A").order_by(Autoridad.clave).all(),
        )
    # Mostrar buscador con la autoridad fija
    form_search.distrito.data = current_user.autoridad.distrito.nombre
    form_search.autoridad.data = current_user.autoridad.descripcion
    return render_template("sentencias/search.jinja2", form=form_search)


@sentencias.route("/sentencias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para sentencias"""
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
    consulta = Sentencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "sentencia" in request.form:
        try:
            sentencia = safe_sentencia(request.form["sentencia"])
            consulta = consulta.filter_by(sentencia=sentencia)
        except (IndexError, ValueError):
            pass
    if "expediente" in request.form:
        try:
            expediente = safe_expediente(request.form["expediente"])
            consulta = consulta.filter_by(expediente=expediente)
        except (IndexError, ValueError):
            pass
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Sentencia.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Sentencia.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(Sentencia.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for sentencia in registros:
        data.append(
            {
                "fecha": sentencia.fecha.strftime("%Y-%m-%d"),
                "detalle": {
                    "sentencia": sentencia.sentencia,
                    "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
                },
                "expediente": sentencia.expediente,
                "es_perspectiva_genero": "Sí" if sentencia.es_perspectiva_genero else "",
                "archivo": {
                    "url": sentencia.url,
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


@sentencias.route("/sentencias/datatable_json_admin", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def datatable_json_admin():
    """DataTable JSON para sentencias admin"""
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
    consulta = Sentencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "sentencia" in request.form:
        try:
            sentencia = safe_sentencia(request.form["sentencia"])
            consulta = consulta.filter_by(sentencia=sentencia)
        except (IndexError, ValueError):
            pass
    if "expediente" in request.form:
        try:
            expediente = safe_expediente(request.form["expediente"])
            consulta = consulta.filter_by(expediente=expediente)
        except (IndexError, ValueError):
            pass
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Sentencia.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Sentencia.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(Sentencia.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for sentencia in registros:
        data.append(
            {
                "creado": sentencia.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": sentencia.autoridad.clave,
                "fecha": sentencia.fecha.strftime("%Y-%m-%d"),
                "detalle": {
                    "sentencia": sentencia.sentencia,
                    "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
                },
                "expediente": sentencia.expediente,
                "es_perspectiva_genero": "Sí" if sentencia.es_perspectiva_genero else "",
                "archivo": {
                    "url": sentencia.url,
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


@sentencias.route("/sentencias/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def refresh(autoridad_id):
    """Refrescar Listas de Acuerdos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("sentencias.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="sentencias.tasks.refrescar",
            descripcion=f"Refrescar sentencias de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("sentencias.list_autoridad_sentencias", autoridad_id=autoridad.id))


@sentencias.route("/sentencias/<int:sentencia_id>")
def detail(sentencia_id):
    """Detalle de un Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    return render_template("sentencias/detail.jinja2", sentencia=sentencia)


def new_success(sentencia):
    """Mensaje de éxito en nueva sentencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Nueva sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Nuevo Sentencia como juzgado"""

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        flash("El juzgado/autoridad no tiene directorio para sentencias.", "warning")
        return redirect(url_for("sentencias.list_active"))

    # Si viene el formulario
    form = SentenciaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True

        # Validar sentencia
        try:
            sentencia_input = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            es_valido = False

        # Validar sentencia_fecha
        sentencia_fecha = form.sentencia_fecha.data
        if not limite_dt <= datetime.datetime(year=sentencia_fecha.year, month=sentencia_fecha.month, day=sentencia_fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            es_valido = False

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            es_valido = False

        # Tomar tipo de juicio
        materia_tipo_juicio = MateriaTipoJuicio.query.get(form.materia_tipo_juicio.data)

        # Tomar descripcion
        descripcion = safe_string(form.descripcion.data, max_len=1020)

        # Tomar perspectiva de género
        es_perspectiva_genero = form.es_perspectiva_genero.data  # Boleano

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            es_valido = False

        if es_valido:
            # Insertar registro
            sentencia = Sentencia(
                autoridad=autoridad,
                materia_tipo_juicio=materia_tipo_juicio,
                sentencia=sentencia_input,
                sentencia_fecha=sentencia_fecha,
                expediente=expediente,
                fecha=fecha,
                descripcion=descripcion,
                es_perspectiva_genero=es_perspectiva_genero,
            )
            sentencia.save()

            # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
            ano_str = fecha.strftime("%Y")
            mes_str = mes_en_palabra(fecha.month)
            fecha_str = fecha.strftime("%Y-%m-%d")
            sentencia_str = sentencia_input.replace("/", "-")
            expediente_str = expediente.replace("/", "-")
            if es_perspectiva_genero:
                archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-G-{sentencia.encode_id()}.pdf"
            else:
                archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-{sentencia.encode_id()}.pdf"
            ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_sentencias, ano_str, mes_str, archivo_str))

            # Subir el archivo
            deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
            storage_client = storage.Client()
            bucket = storage_client.bucket(deposito)
            blob = bucket.blob(ruta_str)
            blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
            url = blob.public_url

            # Actualizar el nombre del archivo y el url
            sentencia.archivo = archivo_str
            sentencia.url = url
            sentencia.save()

            # Mostrar mensaje de éxito e ir al detalle
            bitacora = new_success(sentencia)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template(
        "sentencias/new.jinja2",
        form=form,
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


@sentencias.route("/sentencias/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Sentencia para una autoridad dada"""

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = SentenciaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True

        # Validar sentencia
        try:
            sentencia_input = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            es_valido = False

        # Validar sentencia_fecha
        sentencia_fecha = form.sentencia_fecha.data
        if not limite_dt <= datetime.datetime(year=sentencia_fecha.year, month=sentencia_fecha.month, day=sentencia_fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            es_valido = False

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            es_valido = False

        # Tomar tipo de juicio
        materia_tipo_juicio = MateriaTipoJuicio.query.get(form.materia_tipo_juicio.data)

        # Tomar descripcion
        descripcion = safe_string(form.descripcion.data, max_len=1020)

        # Tomar perspectiva de género
        es_perspectiva_genero = form.es_perspectiva_genero.data  # Boleano

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        if es_valido:
            # Insertar registro
            sentencia = Sentencia(
                autoridad=autoridad,
                materia_tipo_juicio=materia_tipo_juicio,
                sentencia=sentencia_input,
                sentencia_fecha=sentencia_fecha,
                expediente=expediente,
                fecha=fecha,
                descripcion=descripcion,
                es_perspectiva_genero=es_perspectiva_genero,
            )
            sentencia.save()

            # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
            ano_str = fecha.strftime("%Y")
            mes_str = mes_en_palabra(fecha.month)
            fecha_str = fecha.strftime("%Y-%m-%d")
            sentencia_str = sentencia_input.replace("/", "-")
            expediente_str = expediente.replace("/", "-")
            if es_perspectiva_genero:
                archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-{sentencia.encode_id()}.pdf"
            else:
                archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-G-{sentencia.encode_id()}.pdf"
            ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_sentencias, ano_str, mes_str, archivo_str))

            # Subir el archivo
            deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
            storage_client = storage.Client()
            bucket = storage_client.bucket(deposito)
            blob = bucket.blob(ruta_str)
            blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
            url = blob.public_url

            # Actualizar el nombre del archivo y el url
            sentencia.archivo = archivo_str
            sentencia.url = url
            sentencia.save()

            # Mostrar mensaje de éxito e ir al detalle
            bitacora = new_success(sentencia)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template(
        "sentencias/new_for_autoridad.jinja2",
        form=form,
        autoridad=autoridad,
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


@sentencias.route("/sentencias/edicion/<int:sentencia_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit(sentencia_id):
    """Editar Sentencia"""

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar sentencia
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if not (current_user.can_admin("sentencias") or current_user.autoridad_id == sentencia.autoridad_id):
        flash("No tiene permiso para editar esta sentencia.", "warning")
        return redirect(url_for("sentencias.list_active"))

    form = SentenciaEditForm()
    if form.validate_on_submit():
        es_valido = True

        # Validar sentencia
        try:
            sentencia.sentencia = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            es_valido = False

        # Validar sentencia_fecha
        sentencia.sentencia_fecha = form.sentencia_fecha.data
        if not limite_dt <= datetime.datetime(year=sentencia.sentencia_fecha.year, month=sentencia.sentencia_fecha.month, day=sentencia.sentencia_fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            es_valido = False

        # Validar expediente
        try:
            sentencia.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False

        # Validar fecha
        sentencia.fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=sentencia.fecha.year, month=sentencia.fecha.month, day=sentencia.fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            es_valido = False

        # Tomar perspectiva de genero
        sentencia.es_perspectiva_genero = form.es_perspectiva_genero.data

        # Tomar tipo de juicio
        sentencia.materia_tipo_juicio = MateriaTipoJuicio.query.get(form.materia_tipo_juicio.data)

        # Tomar descripcion
        sentencia.descripcion = safe_string(form.descripcion.data, max_len=1020)

        if es_valido:
            sentencia.save()
            bitacora = Bitacora(
                modulo=MODULO,
                usuario=current_user,
                descripcion=safe_message(f"Editada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
                url=url_for("sentencias.detail", sentencia_id=sentencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    form.sentencia.data = sentencia.sentencia
    form.sentencia_fecha.data = sentencia.sentencia_fecha
    form.expediente.data = sentencia.expediente
    form.fecha.data = sentencia.fecha
    form.descripcion.data = sentencia.descripcion
    form.es_perspectiva_genero.data = sentencia.es_perspectiva_genero
    return render_template(
        "sentencias/edit.jinja2",
        form=form,
        sentencia=sentencia,
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


def delete_success(sentencia):
    """Mensaje de éxito al eliminar una sentencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Eliminada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/eliminar/<int:sentencia_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(sentencia_id):
    """Eliminar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("sentencias"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= sentencia.creado:
                sentencia.delete()
                bitacora = delete_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= sentencia.creado:
                sentencia.delete()
                bitacora = delete_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("sentencias.detail", sentencia_id=sentencia_id))


def recover_success(sentencia):
    """Mensaje de éxito al recuperar una sentencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Recuperada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/recuperar/<int:sentencia_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(sentencia_id):
    """Recuperar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("sentencias"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= sentencia.creado:
                sentencia.recover()
                bitacora = recover_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= sentencia.creado:
                sentencia.recover()
                bitacora = recover_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("sentencias.detail", sentencia_id=sentencia_id))
