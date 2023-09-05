"""
Listas de Acuerdos, vistas
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
from lib.safe_string import safe_message, safe_string
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.time_to_text import dia_mes_ano
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.listas_de_acuerdos.forms import ListaDeAcuerdoNewForm, ListaDeAcuerdoMateriaNewForm, ListaDeAcuerdoSearchForm, ListaDeAcuerdoSearchAdminForm, ListaDeAcuerdoReportForm
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.listas_de_acuerdos_acuerdos.models import ListaDeAcuerdoAcuerdo
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

listas_de_acuerdos = Blueprint("listas_de_acuerdos", __name__, template_folder="templates")

HUSO_HORARIO = "America/Mexico_City"
MODULO = "LISTAS DE ACUERDOS"
LIMITE_DIAS = 365  # Es el máximo, aunque autoridad.limite_dias_listas_de_acuerdos sea mayor, gana el menor
LIMITE_ADMINISTRADORES_DIAS = 730  # Administradores pueden manipular dos anios
ORGANOS_JURISDICCIONALES_QUE_PUEDEN_ELEGIR_MATERIA = ("JUZGADO DE PRIMERA INSTANCIA ORAL", "PLENO O SALA DEL TSJ", "TRIBUNAL DISTRITAL")
HORAS_BUENO = 14
HORAS_CRITICO = 16

# Roles que deben estar en la base de datos
ROL_REPORTES_TODOS = ["ADMINISTRADOR", "ESTADISTICA", "VISITADURIA JUDICIAL"]


@listas_de_acuerdos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@listas_de_acuerdos.route("/listas_de_acuerdos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(ListaDeAcuerdo.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(lista_de_acuerdo.creado)
    return render_template("listas_de_acuerdos/checkout.jinja2", lista_de_acuerdo=lista_de_acuerdo, dia=dia, mes=mes.upper(), ano=ano)


@listas_de_acuerdos.route("/listas_de_acuerdos")
def list_active():
    """Listado de Listas de Acuerdos activas"""
    # Si es administrador ve todo
    if current_user.can_admin("LISTAS DE ACUERDOS"):
        return render_template(
            "listas_de_acuerdos/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Listas de Acuerdo",
            estatus="A",
            form=None,
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        form = ListaDeAcuerdoReportForm()
        form.autoridad_id.data = autoridad.id  # Oculto la autoridad del usuario
        form.fecha_desde.data = datetime.date.today().replace(day=1)  # Por defecto fecha_desde es el primer dia del mes actual
        form.fecha_hasta.data = datetime.date.today()  # Por defecto fecha_hasta es hoy
        return render_template(
            "listas_de_acuerdos/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Listas de Acuerdos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
            form=form,
        )
    # Ninguno de los anteriores
    return redirect(url_for("listas_de_acuerdos.list_distritos"))


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Listas de Acuerdos inactivas"""
    # Si es administrador ve todo
    if current_user.can_admin("LISTAS DE ACUERDOS"):
        return render_template(
            "listas_de_acuerdos/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todas las Listas de Acuerdos inactivas",
            estatus="B",
            form=None,
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "listas_de_acuerdos/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Listas de Acuerdos inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
            form=None,
        )
    # Ninguno de los anteriores
    return redirect(url_for("listas_de_acuerdos.list_distritos"))


@listas_de_acuerdos.route("/listas_de_acuerdos/distritos")
def list_distritos():
    """Listado de Distritos"""
    return render_template(
        "listas_de_acuerdos/list_distritos.jinja2",
        distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
    )


@listas_de_acuerdos.route("/listas_de_acuerdos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template(
        "listas_de_acuerdos/list_autoridades.jinja2",
        distrito=distrito,
        autoridades=Autoridad.query.filter(Autoridad.distrito == distrito).filter_by(es_jurisdiccional=True).filter_by(es_notaria=False).filter_by(estatus="A").order_by(Autoridad.clave).all(),
    )


@listas_de_acuerdos.route("/listas_de_acuerdos/autoridad/<int:autoridad_id>")
def list_autoridad_listas_de_acuerdos(autoridad_id):
    """Listado de Listas de Acuerdos activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = None
    plantilla = "listas_de_acuerdos/list.jinja2"
    if current_user.can_admin("LISTAS DE ACUERDOS") or set(current_user.get_roles()).intersection(set(ROL_REPORTES_TODOS)):
        plantilla = "listas_de_acuerdos/list_admin.jinja2"
        form = ListaDeAcuerdoReportForm()
        form.autoridad_id.data = autoridad.id  # Oculto la autoridad que esta viendo
        form.fecha_desde.data = datetime.date.today().replace(day=1)  # Por defecto fecha_desde es el primer dia del mes actual
        form.fecha_hasta.data = datetime.date.today()  # Por defecto fecha_hasta es hoy
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Listas de Acuerdos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
        form=form,
    )


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_autoridad_listas_de_acuerdos_inactive(autoridad_id):
    """Listado de Listas de Acuerdos inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("LISTAS DE ACUERDOS"):
        plantilla = "listas_de_acuerdos/list_admin.jinja2"
    else:
        plantilla = "listas_de_acuerdos/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Listas de Acuerdos inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
        form=None,
    )


@listas_de_acuerdos.route("/listas_de_acuerdos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Lista de Acuerdos"""
    if current_user.can_admin("LISTAS DE ACUERDOS"):
        puede_elegir_autoridad = True
    elif current_user.autoridad.es_jurisdiccional:
        puede_elegir_autoridad = False
    else:
        puede_elegir_autoridad = True
    if puede_elegir_autoridad:
        form_search = ListaDeAcuerdoSearchAdminForm()
    else:
        form_search = ListaDeAcuerdoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        fallo_validacion = False
        # Autoridad es un campo obligatorio
        if puede_elegir_autoridad:
            autoridad = Autoridad.query.get(form_search.autoridad.data)
            plantilla = "listas_de_acuerdos/list_admin.jinja2"
        else:
            autoridad = current_user.autoridad
            plantilla = "listas_de_acuerdos/list.jinja2"
        busqueda["autoridad_id"] = autoridad.id
        titulos.append(autoridad.distrito.nombre_corto + ", " + autoridad.descripcion_corta)
        # Fecha
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
                titulo="Listas de Acuerdos con " + ", ".join(titulos),
            )
    # Mostrar buscador donde puede elegir la autoridad
    if puede_elegir_autoridad:
        return render_template(
            "listas_de_acuerdos/search_admin.jinja2",
            form=form_search,
            distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
            autoridades=Autoridad.query.filter_by(es_jurisdiccional=True).filter_by(es_notaria=False).filter_by(estatus="A").order_by(Autoridad.clave).all(),
        )
    # Mostrar buscador con la autoridad fija
    form_search.distrito.data = current_user.autoridad.distrito.nombre
    form_search.autoridad.data = current_user.autoridad.descripcion
    return render_template("listas_de_acuerdos/search.jinja2", form=form_search)


@listas_de_acuerdos.route("/listas_de_acuerdos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de listas de acuerdos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ListaDeAcuerdo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ListaDeAcuerdo.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ListaDeAcuerdo.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(ListaDeAcuerdo.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Zona horaria local
    local_tz = timezone(HUSO_HORARIO)
    # Medianoche en HH:MM:SS
    medianoche = datetime.time.min
    # Elaborar datos para DataTable
    data = []
    for lista_de_acuerdo in registros:
        # La columna creado esta en UTC, convertir a local
        creado_local = lista_de_acuerdo.creado.astimezone(local_tz)
        # Determinar el tiempo bueno
        tiempo_limite_bueno = datetime.datetime.combine(
            lista_de_acuerdo.fecha,
            medianoche,
        ) + datetime.timedelta(hours=HORAS_BUENO)
        # Determinar el fiempo critico
        tiempo_limite_critico = datetime.datetime.combine(
            lista_de_acuerdo.fecha,
            medianoche,
        ) + datetime.timedelta(hours=HORAS_CRITICO)
        # Por defecto el semaforo es verde (0)
        semaforo = 0
        # Si creado_local es mayor a tiempo_limite_bueno, entonces el semaforo es amarillo (1)
        if creado_local > local_tz.localize(tiempo_limite_bueno):
            semaforo = 1
        # Si creado_local es mayor a tiempo_limite_critico, entonces el semaforo es rojo (2)
        if creado_local > local_tz.localize(tiempo_limite_critico):
            semaforo = 2
        data.append(
            {
                "creado": {
                    "tiempo": creado_local.strftime("%Y-%m-%d %H:%M"),
                    "semaforo": semaforo,
                },
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "detalle": {
                    "descripcion": lista_de_acuerdo.descripcion,
                    "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
                },
                "archivo": {
                    "descargar_url": lista_de_acuerdo.descargar_url,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@listas_de_acuerdos.route("/listas_de_acuerdos/datatable_json_admin", methods=["GET", "POST"])
def datatable_json_admin():
    """DataTable JSON para listado de listas de acuerdos admin"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ListaDeAcuerdo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ListaDeAcuerdo.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ListaDeAcuerdo.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(ListaDeAcuerdo.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Zona horaria local
    local_tz = timezone(HUSO_HORARIO)
    # Medianoche en HH:MM:SS
    medianoche = datetime.time.min
    # Elaborar datos para DataTable
    data = []
    for lista_de_acuerdo in registros:
        # La columna creado esta en UTC, convertir a local
        creado_local = lista_de_acuerdo.creado.astimezone(local_tz)
        # Determinar el tiempo bueno
        tiempo_limite_bueno = datetime.datetime.combine(
            lista_de_acuerdo.fecha,
            medianoche,
        ) + datetime.timedelta(hours=HORAS_BUENO)
        # Determinar el fiempo critico
        tiempo_limite_critico = datetime.datetime.combine(
            lista_de_acuerdo.fecha,
            medianoche,
        ) + datetime.timedelta(hours=HORAS_CRITICO)
        # Por defecto el semaforo es verde (0)
        semaforo = 0
        # Si la autoridad tiene limite_dias_listas_de_acuerdos igual a cero
        if lista_de_acuerdo.autoridad.limite_dias_listas_de_acuerdos == 0:
            # Si creado_local es mayor a tiempo_limite_bueno, entonces el semaforo es amarillo (1)
            if creado_local > local_tz.localize(tiempo_limite_bueno):
                semaforo = 1
            # Si creado_local es mayor a tiempo_limite_critico, entonces el semaforo es rojo (2)
            if creado_local > local_tz.localize(tiempo_limite_critico):
                semaforo = 2
        data.append(
            {
                "detalle": {
                    "id": lista_de_acuerdo.id,
                    "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
                },
                "creado": {
                    "tiempo": creado_local.strftime("%Y-%m-%d %H:%M"),
                    "semaforo": semaforo,
                },
                "autoridad": lista_de_acuerdo.autoridad.clave,
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "descripcion": lista_de_acuerdo.descripcion,
                "archivo": {
                    "descargar_url": url_for("listas_de_acuerdos.download", url=quote(lista_de_acuerdo.url)),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@listas_de_acuerdos.route("/listas_de_acuerdos/descargar", methods=["GET"])
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
        archivo = get_file_from_gcs(current_app.config["CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS"], blob_name)
    except MyAnyError as error:
        flash(str(error), "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    # Entregar archivo
    return current_app.response_class(archivo, mimetype=media_type)


@listas_de_acuerdos.route("/listas_de_acuerdos/refrescar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def refresh(autoridad_id):
    """Refrescar Listas de Acuerdos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("listas_de_acuerdos.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="listas_de_acuerdos.tasks.refrescar",
            descripcion=f"Refrescar listas de acuerdos de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("listas_de_acuerdos.list_autoridad_listas_de_acuerdos", autoridad_id=autoridad.id))


@listas_de_acuerdos.route("/listas_de_acuerdos/<int:lista_de_acuerdo_id>")
def detail(lista_de_acuerdo_id):
    """Detalle de una Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    acuerdos = None  # Por lo pronto sólo los administradores ven los acuerdos
    if current_user.can_admin("LISTAS DE ACUERDOS"):
        acuerdos = ListaDeAcuerdoAcuerdo.query.filter(ListaDeAcuerdoAcuerdo.lista_de_acuerdo == lista_de_acuerdo).filter_by(estatus="A").all()
    return render_template("listas_de_acuerdos/detail.jinja2", lista_de_acuerdo=lista_de_acuerdo, acuerdos=acuerdos)


def new_success(lista_de_acuerdo, anterior_borrada=None):
    """Mensaje de éxito en nueva lista de acuerdos"""
    if anterior_borrada:
        mensaje = "Reemplazada "
    else:
        mensaje = "Nueva "
    mensaje = mensaje + f"lista de acuerdos del {lista_de_acuerdo.fecha.strftime('%Y-%m-%d')} de {lista_de_acuerdo.autoridad.clave}"
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(mensaje),
        url=url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
    )
    bitacora.save()
    return bitacora


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Subir Lista de Acuerdos como juzgado"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        flash("El juzgado/autoridad no tiene directorio para listas de acuerdos.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))

    # Google App Engine usa tiempo universal, sin esta correccion las fechas de la noche cambian al dia siguiente
    ahora_utc = datetime.datetime.now(timezone("UTC"))
    ahora_mx_coah = ahora_utc.astimezone(timezone(HUSO_HORARIO))

    # Para validar la fecha
    hoy = ahora_mx_coah.date()
    hoy_dt = ahora_mx_coah
    if autoridad.limite_dias_listas_de_acuerdos < LIMITE_DIAS:
        mi_limite_dias = autoridad.limite_dias_listas_de_acuerdos
    else:
        mi_limite_dias = LIMITE_DIAS
    if mi_limite_dias > 0:
        limite_dt = hoy_dt + datetime.timedelta(days=-mi_limite_dias)
    else:
        limite_dt = hoy_dt

    # Decidir entre formulario sin materia o con materia
    con_materia = autoridad.organo_jurisdiccional in ORGANOS_JURISDICCIONALES_QUE_PUEDEN_ELEGIR_MATERIA
    if con_materia:
        form = ListaDeAcuerdoMateriaNewForm(CombinedMultiDict((request.files, request.form)))
    else:
        form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))

    # Si viene el formulario
    if form.validate_on_submit():
        es_valido = True

        # Validar fecha
        if mi_limite_dias > 0:
            fecha = form.fecha.data
            if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day, tzinfo=timezone(HUSO_HORARIO)) <= hoy_dt:
                flash(f"La fecha no debe ser del futuro ni anterior a {mi_limite_dias} días.", "warning")
                es_valido = False
        else:
            fecha = hoy

        # Inicializar la liberia Google Cloud Storage con el directorio base, la fecha, las extensiones permitidas y los meses como palabras
        gcstorage = GoogleCloudStorage(
            base_directory=autoridad.directorio_listas_de_acuerdos,
            upload_date=fecha,
            allowed_extensions=["pdf"],
            month_in_word=True,
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS"],
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

        # No es válido, entonces se vuelve a mostrar el formulario
        if es_valido is False:
            return render_template("listas_de_acuerdos/new.jinja2", form=form, mi_limite_dias=mi_limite_dias, con_materia=con_materia)

        # Definir descripcion
        descripcion = "LISTA DE ACUERDOS"
        if con_materia:
            materia = form.materia.data
            if materia.id != 1:  # NO DEFINIDO
                descripcion = safe_string(f"LISTA DE ACUERDOS {materia.nombre}")

        # Si existe una lista de acuerdos de la misma fecha, dar de baja la antigua
        anterior_borrada = False
        if con_materia is False:
            anterior_lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.fecha == fecha).filter_by(estatus="A").first()
            if anterior_lista_de_acuerdo:
                anterior_lista_de_acuerdo.delete()
                anterior_borrada = True
        else:
            anterior_lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.fecha == fecha).filter_by(descripcion=descripcion).filter_by(estatus="A").first()
            if anterior_lista_de_acuerdo:
                anterior_lista_de_acuerdo.delete()
                anterior_borrada = True

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Subir a Google Cloud Storage
        es_exitoso = True
        try:
            gcstorage.set_filename(hashed_id=lista_de_acuerdo.encode_id(), description=descripcion)
            gcstorage.upload(archivo.stream.read())
        except NotConfiguredError:
            flash("Error al subir el archivo porque falla la configuración.", "danger")
            es_exitoso = False
        except Exception:
            flash("Error al subir el archivo.", "danger")
            es_exitoso = False

        # Si se sube con exito, actualizar el registro con la URL del archivo y mostrar el detalle
        if es_exitoso:
            lista_de_acuerdo.archivo = gcstorage.filename
            lista_de_acuerdo.url = gcstorage.url
            lista_de_acuerdo.save()
            bitacora = new_success(lista_de_acuerdo, anterior_borrada)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Llenar de los campos del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy

    # Si puede elegir la materia
    if con_materia:
        form.materia.data = Materia.query.get(1)  # Por defecto NO DEFINIDO

    # Mostrar formulario
    return render_template("listas_de_acuerdos/new.jinja2", form=form, mi_limite_dias=mi_limite_dias, con_materia=con_materia)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def new_for_autoridad(autoridad_id):
    """Subir Lista de Acuerdos para una autoridad dada"""

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Decidir entre formulario sin materia o con materia
    con_materia = autoridad.organo_jurisdiccional in ORGANOS_JURISDICCIONALES_QUE_PUEDEN_ELEGIR_MATERIA
    if con_materia:
        form = ListaDeAcuerdoMateriaNewForm(CombinedMultiDict((request.files, request.form)))
    else:
        form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))

    # Si viene el formulario
    if form.validate_on_submit():
        es_valido = True

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            es_valido = False

        # Inicializar la liberia Google Cloud Storage con el directorio base, la fecha, las extensiones permitidas y los meses como palabras
        gcstorage = GoogleCloudStorage(
            base_directory=autoridad.directorio_listas_de_acuerdos,
            upload_date=fecha,
            allowed_extensions=["pdf"],
            month_in_word=True,
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS"],
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

        # No es válido, entonces se vuelve a mostrar el formulario
        if es_valido is False:
            return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad, con_materia=con_materia)

        # Definir descripcion
        descripcion = "LISTA DE ACUERDOS"
        if con_materia:
            materia = form.materia.data
            if materia.id != 1:  # NO DEFINIDO
                descripcion = safe_string(f"LISTA DE ACUERDOS {materia.nombre}")

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Subir a Google Cloud Storage
        es_exitoso = True
        try:
            gcstorage.set_filename(hashed_id=lista_de_acuerdo.encode_id(), description=descripcion)
            gcstorage.upload(archivo.stream.read())
        except NotConfiguredError:
            flash("Error al subir el archivo porque falla la configuración.", "danger")
            es_exitoso = False
        except Exception:
            flash("Error al subir el archivo.", "danger")
            es_exitoso = False

        # Si se sube con exito, actualizar el registro y mostrar el detalle
        if es_exitoso:
            lista_de_acuerdo.archivo = gcstorage.filename
            lista_de_acuerdo.url = gcstorage.url
            lista_de_acuerdo.save()
            bitacora = new_success(lista_de_acuerdo)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy

    # Si puede elegir la materia
    if con_materia:
        form.materia.data = Materia.query.get(1)  # Por defecto NO DEFINIDO

    # Mostrar formulario
    return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad, con_materia=con_materia)


def delete_success(lista_de_acuerdo):
    """Mensaje de éxito al eliminar una lista de acuerdos"""
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Eliminada la lista de acuerdos del {lista_de_acuerdo.fecha.strftime('%Y-%m-%d')} de {lista_de_acuerdo.autoridad.clave}"),
        url=url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
    )
    bitacora.save()
    return bitacora


@listas_de_acuerdos.route("/listas_de_acuerdos/eliminar/<int:lista_de_acuerdo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(lista_de_acuerdo_id):
    """Eliminar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "A":
        if current_user.can_admin("LISTAS DE ACUERDOS"):
            hoy = datetime.date.today()
            hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
            limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
            if limite_dt.timestamp() <= lista_de_acuerdo.creado.timestamp():
                lista_de_acuerdo.delete()
                bitacora = delete_success(lista_de_acuerdo)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == lista_de_acuerdo.autoridad_id and lista_de_acuerdo.fecha == datetime.date.today():
            lista_de_acuerdo.delete()
            bitacora = delete_success(lista_de_acuerdo)
            flash(bitacora.descripcion, "success")
        else:
            flash("No tiene permiso para eliminar o sólo puede eliminar de hoy.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


def recover_success(lista_de_acuerdo):
    """Mensaje de éxito al recuperar una lista de acuerdos"""
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Recuperada la lista de acuerdos del {lista_de_acuerdo.fecha.strftime('%Y-%m-%d')} de {lista_de_acuerdo.autoridad.clave}"),
        url=url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
    )
    bitacora.save()
    return bitacora


@listas_de_acuerdos.route("/listas_de_acuerdos/recuperar/<int:lista_de_acuerdo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(lista_de_acuerdo_id):
    """Recuperar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "B":
        if ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == current_user.autoridad).filter(ListaDeAcuerdo.fecha == lista_de_acuerdo.fecha).filter_by(estatus="A").first():
            flash("No puede recuperar esta lista porque ya hay una activa de la misma fecha.", "warning")
        else:
            if current_user.can_admin("LISTAS DE ACUERDOS"):
                hoy = datetime.date.today()
                hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
                limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)
                if limite_dt.timestamp() <= lista_de_acuerdo.creado.timestamp():
                    lista_de_acuerdo.recover()
                    bitacora = recover_success(lista_de_acuerdo)
                    flash(bitacora.descripcion, "success")
                else:
                    flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
            elif current_user.autoridad_id == lista_de_acuerdo.autoridad_id and lista_de_acuerdo.fecha == datetime.date.today():
                lista_de_acuerdo.recover()
                bitacora = recover_success(lista_de_acuerdo)
                flash(bitacora.descripcion, "success")
            else:
                flash("No tiene permiso para recuperar o sólo puede recuperar de hoy.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


@listas_de_acuerdos.route("/listas_de_acuerdos/reporte", methods=["GET", "POST"])
def report():
    """Elaborar reporte de listas de acuerdos"""
    # Preparar el formulario
    form = ListaDeAcuerdoReportForm()
    # Si viene el formulario
    if form.validate():
        # Tomar los valores del formulario
        autoridad = Autoridad.query.get_or_404(int(form.autoridad_id.data))
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        # Si la fecha_desde es posterior a la fecha_hasta, se intercambian
        if fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde
        # Si no es administrador, ni tiene un rol para elaborar reportes de todos
        if not current_user.can_admin("LISTAS DE ACUERDOS") and not set(current_user.get_roles()).intersection(set(ROL_REPORTES_TODOS)):
            # Si la autoridad del usuario no es la del formulario, se niega el acceso
            if current_user.autoridad_id != autoridad.id:
                flash("No tiene permiso para acceder a este reporte.", "warning")
                return redirect(url_for("listas_de_acuerdos.list_active"))
        # Entregar el reporte
        return render_template(
            "listas_de_acuerdos/report.jinja2",
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
    flash("Error: datos incorrectos para hacer el reporte.", "warning")
    return redirect(url_for("listas_de_acuerdos.list_active"))
