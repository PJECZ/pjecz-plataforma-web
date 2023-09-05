"""
Sentencias, vistas
"""
import datetime
import json
from urllib.parse import quote

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from pytz import timezone
from werkzeug.datastructures import CombinedMultiDict

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.exceptions import MyAnyError
from lib.google_cloud_storage import get_blob_name_from_url, get_media_type_from_filename, get_file_from_gcs
from lib.safe_string import extract_expediente_anio, extract_expediente_num, safe_expediente, safe_message, safe_sentencia, safe_string
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.time_to_text import dia_mes_ano
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.sentencias.forms import SentenciaNewForm, SentenciaEditForm, SentenciaSearchForm, SentenciaSearchAdminForm, SentenciaReportForm
from plataforma_web.blueprints.sentencias.models import Sentencia

sentencias = Blueprint("sentencias", __name__, template_folder="templates")

HUSO_HORARIO = "America/Mexico_City"
MODULO = "SENTENCIAS"
LIMITE_DIAS = 10950  # 30 años
LIMITE_ADMINISTRADORES_DIAS = 10950  # 30 años

# Roles que deben estar en la base de datos
ROL_REPORTES_TODOS = ["ADMINISTRADOR", "ESTADISTICA", "VISITADURIA JUDICIAL"]


@sentencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@sentencias.route("/sentencias/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    sentencia = Sentencia.query.get_or_404(Sentencia.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(sentencia.creado)
    return render_template("sentencias/checkout.jinja2", sentencia=sentencia, dia=dia, mes=mes.upper(), ano=ano)


@sentencias.route("/sentencias")
def list_active():
    """Listado de Sentencias activas más recientes"""
    # Si es administrador ve todo
    if current_user.can_admin("SENTENCIAS"):
        return render_template(
            "sentencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las V.P. de Sentencias",
            estatus="A",
            form=None,
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        form = SentenciaReportForm()
        form.autoridad_id.data = autoridad.id  # Oculto la autoridad del usuario
        form.fecha_desde.data = datetime.date.today().replace(day=1)  # Por defecto fecha_desde es el primer dia del mes actual
        form.fecha_hasta.data = datetime.date.today()  # Por defecto fecha_hasta es hoy
        return render_template(
            "sentencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"V.P. de Sentencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
            form=form,
        )
    # Ninguno de los anteriores
    return redirect(url_for("sentencias.list_distritos"))


@sentencias.route("/sentencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Sentencias inactivas"""
    # Si es administrador ve todo
    if current_user.can_admin("SENTENCIAS"):
        return render_template(
            "sentencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todas las V.P. de Sentencias inactivas",
            estatus="B",
            form=None,
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "sentencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"V.P. de Sentencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
            form=None,
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
    form = None
    plantilla = "sentencias/list.jinja2"
    if current_user.can_admin("SENTENCIAS") or set(current_user.get_roles()).intersection(set(ROL_REPORTES_TODOS)):
        plantilla = "sentencias/list_admin.jinja2"
        form = SentenciaReportForm()
        form.autoridad_id.data = autoridad.id  # Oculto la autoridad que esta viendo
        form.fecha_desde.data = datetime.date.today().replace(day=1)  # Por defecto fecha_desde es el primer dia del mes actual
        form.fecha_hasta.data = datetime.date.today()  # Por defecto fecha_hasta es hoy
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"V.P. de Sentencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
        form=form,
    )


@sentencias.route("/sentencias/inactivos/autoridad/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_autoridad_sentencias_inactive(autoridad_id):
    """Listado de Sentencias inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("SENTENCIAS"):
        plantilla = "sentencias/list_admin.jinja2"
    else:
        plantilla = "sentencias/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"V.P. de Sentencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
        form=None,
    )


@sentencias.route("/sentencias/buscar", methods=["GET", "POST"])
def search():
    """Buscar Sentencias"""
    if current_user.can_admin("SENTENCIAS"):
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
        # Es perspectiva de genero
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
    draw, start, rows_per_page = get_datatable_parameters()
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
                "materia_nombre": sentencia.materia_tipo_juicio.materia.nombre,
                "materia_tipo_juicio_descripcion": sentencia.materia_tipo_juicio.descripcion,
                "es_perspectiva_genero": "Sí" if sentencia.es_perspectiva_genero else "",
                "archivo": {
                    "descargar_url": sentencia.descargar_url,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@sentencias.route("/sentencias/datatable_json_admin", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def datatable_json_admin():
    """DataTable JSON para sentencias admin"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
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
    registros = consulta.order_by(Sentencia.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Zona horaria local
    local_tz = timezone(HUSO_HORARIO)
    # Elaborar datos para DataTable
    data = []
    for sentencia in registros:
        creado_local = sentencia.creado.astimezone(local_tz)  # La columna creado esta en UTC, convertir a local
        data.append(
            {
                "detalle": {
                    "id": sentencia.id,
                    "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
                },
                "creado": creado_local.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": sentencia.autoridad.clave,
                "fecha": sentencia.fecha.strftime("%Y-%m-%d"),
                "sentencia": sentencia.sentencia,
                "expediente": sentencia.expediente,
                "materia_nombre": sentencia.materia_tipo_juicio.materia.nombre,
                "materia_tipo_juicio_descripcion": sentencia.materia_tipo_juicio.descripcion,
                "es_perspectiva_genero": "Sí" if sentencia.es_perspectiva_genero else "",
                "archivo": {
                    "descargar_url": url_for("sentencias.download", url=quote(sentencia.url)),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@sentencias.route("/sentencias/descargar", methods=["GET"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def download():
    """Descargar archivo desde Google Cloud Storage"""
    url = request.args.get("url")
    try:
        # Obtener nombre del blob
        blob_name = get_blob_name_from_url(url)
        # Obtener tipo de media
        media_type = get_media_type_from_filename(blob_name)
        # Obtener archivo
        archivo = get_file_from_gcs(current_app.config["CLOUD_STORAGE_DEPOSITO_SENTENCIAS"], blob_name)
    except MyAnyError as error:
        flash(str(error), "warning")
        return redirect(url_for("sentencias.list_active"))
    # Entregar archivo
    return current_app.response_class(archivo, mimetype=media_type)


@sentencias.route("/sentencias/refrescar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
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
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Nueva sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Subir Sentencia como juzgado"""

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

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

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
        descripcion = safe_string(form.descripcion.data, max_len=1000)

        # Tomar perspectiva de género
        es_perspectiva_genero = form.es_perspectiva_genero.data  # Boleano

        # Inicializar la liberia Google Cloud Storage con el directorio base, la fecha, las extensiones permitidas y los meses como palabras
        gcstorage = GoogleCloudStorage(
            base_directory=autoridad.directorio_sentencias,
            upload_date=fecha,
            allowed_extensions=["pdf"],
            month_in_word=True,
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_SENTENCIAS"],
        )

        # Validar archivo
        archivo = request.files["archivo"]
        try:
            gcstorage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False

        # Si es valido
        if es_valido:
            # Insertar registro
            sentencia = Sentencia(
                autoridad=autoridad,
                materia_tipo_juicio=materia_tipo_juicio,
                sentencia=sentencia_input,
                sentencia_fecha=sentencia_fecha,
                expediente=expediente,
                expediente_anio=extract_expediente_anio(expediente),
                expediente_num=extract_expediente_num(expediente),
                fecha=fecha,
                descripcion=descripcion,
                es_perspectiva_genero=es_perspectiva_genero,
            )
            sentencia.save()

            # El nombre del archivo contiene FECHA/SENTENCIA/EXPEDIENTE/PERSPECTIVA_GENERO/HASH
            nombre_elementos = []
            nombre_elementos.append(sentencia_input.replace("/", "-"))
            nombre_elementos.append(expediente.replace("/", "-"))
            if es_perspectiva_genero:
                nombre_elementos.append("G")

            # Subir a Google Cloud Storage
            es_exitoso = True
            try:
                gcstorage.set_filename(
                    hashed_id=sentencia.encode_id(),
                    description="-".join(nombre_elementos),
                )
                gcstorage.upload(archivo.stream.read())
            except NotConfiguredError:
                flash("Error al subir el archivo porque falla la configuración.", "danger")
                es_exitoso = False
            except Exception:
                flash("Error al subir el archivo.", "danger")
                es_exitoso = False

            # Si se sube con exito, actualizar el registro con la URL del archivo y mostrar el detalle
            if es_exitoso:
                sentencia.archivo = gcstorage.filename
                sentencia.url = gcstorage.url
                sentencia.save()
                bitacora = new_success(sentencia)
                flash(bitacora.descripcion, "success")
                return redirect(bitacora.url)

    # Llenar de los campos del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy

    # Mostrar formulario
    return render_template(
        "sentencias/new.jinja2",
        form=form,
        autoridad=autoridad,
        materias=Materia.query.filter_by(en_sentencias=True).filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


@sentencias.route("/sentencias/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def new_for_autoridad(autoridad_id):
    """Subir Sentencia para una autoridad dada"""

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

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

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
        descripcion = safe_string(form.descripcion.data, max_len=1000)

        # Tomar perspectiva de género
        es_perspectiva_genero = form.es_perspectiva_genero.data  # Boleano

        # Inicializar la liberia Google Cloud Storage con el directorio base, la fecha, las extensiones permitidas y los meses como palabras
        gcstorage = GoogleCloudStorage(
            base_directory=autoridad.directorio_sentencias,
            upload_date=fecha,
            allowed_extensions=["pdf"],
            month_in_word=True,
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_SENTENCIAS"],
        )

        # Validar archivo
        archivo = request.files["archivo"]
        try:
            gcstorage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False

        # Si es valido
        if es_valido:
            # Insertar registro
            sentencia = Sentencia(
                autoridad=autoridad,
                materia_tipo_juicio=materia_tipo_juicio,
                sentencia=sentencia_input,
                sentencia_fecha=sentencia_fecha,
                expediente=expediente,
                expediente_anio=extract_expediente_anio(expediente),
                expediente_num=extract_expediente_num(expediente),
                fecha=fecha,
                descripcion=descripcion,
                es_perspectiva_genero=es_perspectiva_genero,
            )
            sentencia.save()

            # El nombre del archivo contiene FECHA/SENTENCIA/EXPEDIENTE/PERSPECTIVA_GENERO/HASH
            nombre_elementos = []
            nombre_elementos.append(sentencia_input.replace("/", "-"))
            nombre_elementos.append(expediente.replace("/", "-"))
            if es_perspectiva_genero:
                nombre_elementos.append("G")

            # Subir a Google Cloud Storage
            es_exitoso = True
            try:
                gcstorage.set_filename(
                    hashed_id=sentencia.encode_id(),
                    description="-".join(nombre_elementos),
                )
                gcstorage.upload(archivo.stream.read())
            except NotConfiguredError:
                flash("Error al subir el archivo porque falla la configuración.", "danger")
                es_exitoso = False
            except Exception:
                flash("Error al subir el archivo.", "danger")
                es_exitoso = False

            # Si se sube con exito, actualizar el registro y mostrar el detalle
            if es_exitoso:
                sentencia.archivo = gcstorage.filename
                sentencia.url = gcstorage.url
                sentencia.save()
                bitacora = new_success(sentencia)
                flash(bitacora.descripcion, "success")
                return redirect(bitacora.url)

    # Llenar de los campos del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy

    # Mostrar formulario
    return render_template(
        "sentencias/new_for_autoridad.jinja2",
        form=form,
        autoridad=autoridad,
        materias=Materia.query.filter_by(en_sentencias=True).filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


@sentencias.route("/sentencias/edicion/<int:sentencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def edit(sentencia_id):
    """Editar Sentencia"""

    # Para validar las fechas
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar sentencia
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if not (current_user.can_admin("SENTENCIAS") or current_user.autoridad_id == sentencia.autoridad_id):
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
            sentencia.expediente_anio = extract_expediente_anio(sentencia.expediente)
            sentencia.expediente_num = extract_expediente_num(sentencia.expediente)
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
        sentencia.descripcion = safe_string(form.descripcion.data, max_len=1000)

        if es_valido:
            sentencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
                url=url_for("sentencias.detail", sentencia_id=sentencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Llenar de los campos del formulario
    form.sentencia.data = sentencia.sentencia
    form.sentencia_fecha.data = sentencia.sentencia_fecha
    form.expediente.data = sentencia.expediente
    form.fecha.data = sentencia.fecha
    form.descripcion.data = sentencia.descripcion
    form.es_perspectiva_genero.data = sentencia.es_perspectiva_genero

    # Mostrar formulario
    return render_template(
        "sentencias/edit.jinja2",
        form=form,
        sentencia=sentencia,
        materias=Materia.query.filter_by(en_sentencias=True).filter_by(estatus="A").order_by(Materia.id).all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.materia_id, MateriaTipoJuicio.descripcion).all(),
    )


def delete_success(sentencia):
    """Mensaje de éxito al eliminar una sentencia"""
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Eliminada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/eliminar/<int:sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(sentencia_id):
    """Eliminar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("SENTENCIAS"):
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
            if limite_dt.timestamp() <= sentencia.creado.timestamp():
                sentencia.delete()
                bitacora = delete_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)
            if limite_dt.timestamp() <= sentencia.creado.timestamp():
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
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Recuperada la sentencia {sentencia.sentencia}, expediente {sentencia.expediente} de {sentencia.autoridad.clave}"),
        url=url_for("sentencias.detail", sentencia_id=sentencia.id),
    )
    bitacora.save()
    return bitacora


@sentencias.route("/sentencias/recuperar/<int:sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(sentencia_id):
    """Recuperar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("SENTENCIAS"):
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
            if limite_dt.timestamp() <= sentencia.creado.timestamp():
                sentencia.recover()
                bitacora = recover_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)
            if limite_dt.timestamp() <= sentencia.creado.timestamp():
                sentencia.recover()
                bitacora = recover_success(sentencia)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("sentencias.detail", sentencia_id=sentencia_id))


@sentencias.route("/sentencias/reporte", methods=["GET", "POST"])
def report():
    """Elaborar reporte de sentencias"""
    # Preparar el formulario
    form = SentenciaReportForm()
    # Si viene el formulario
    if form.validate():
        # Tomar valores del formulario
        autoridad = Autoridad.query.get_or_404(int(form.autoridad_id.data))
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        # Si no es administrador, ni tiene un rol para elaborar reportes de todos
        if not current_user.can_admin("SENTENCIAS") and not set(current_user.get_roles()).intersection(set(ROL_REPORTES_TODOS)):
            # Si la autoridad del usuario no es la del formulario, se niega el acceso
            if current_user.autoridad_id != autoridad.id:
                flash("No tiene permiso para acceder a este reporte.", "warning")
                return redirect(url_for("listas_de_acuerdos.list_active"))
        # Entregar pagina
        return render_template(
            "sentencias/report.jinja2",
            autoridad=autoridad,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            filtros=json.dumps(
                {
                    "autoridad_id": autoridad.id,
                    "estatus": "A",
                    "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                    "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
                }
            ),
        )
    # No viene el formulario, por lo tanto se advierte del error
    flash("Error: datos incorrectos para hacer la descarga.", "warning")
    return redirect(url_for("sentencias.list_active"))
