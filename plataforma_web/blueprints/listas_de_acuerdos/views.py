"""
Listas de Acuerdos, vistas
"""
import datetime
from pathlib import Path
from unidecode import unidecode

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.forms import ListaDeAcuerdoNewForm, ListaDeAcuerdoEditForm, ListaDeAcuerdoSearchForm
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo, ListaDeAcuerdoException

from plataforma_web.blueprints.autoridades.models import Autoridad, AutoridadException
from plataforma_web.blueprints.distritos.models import Distrito

listas_de_acuerdos = Blueprint("listas_de_acuerdos", __name__, template_folder="templates")

SUBDIRECTORIO = "Listas de Acuerdos"


@listas_de_acuerdos.route("/listas_de_acuerdos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(ListaDeAcuerdo.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(lista_de_acuerdo.creado)
    return render_template("listas_de_acuerdos/checkout.jinja2", lista_de_acuerdo=lista_de_acuerdo, dia=dia, mes=mes.upper(), ano=ano)


@listas_de_acuerdos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@listas_de_acuerdos.route("/listas_de_acuerdos")
def list_active():
    """Listado de Listas de Acuerdos activas más recientes"""
    # Si es administrador, ve las listas de acuerdos de todas las autoridades
    if current_user.can_admin("listas_de_acuerdos"):
        todas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list_admin.jinja2", autoridad=None, listas_de_acuerdos=todas, estatus="A")
    # No es administrador, consultar su autoridad
    autoridad = Autoridad.query.get_or_404(current_user.autoridad_id)
    # Si su autoridad es jurisdiccional, ve sus propias listas de acuerdos
    if current_user.autoridad.es_jurisdiccional:
        sus_listas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=sus_listas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("listas_de_acuerdos.list_distritos"))


@listas_de_acuerdos.route("/listas_de_acuerdos/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("listas_de_acuerdos/list_distritos.jinja2", distritos=distritos, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("listas_de_acuerdos/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/autoridad/<int:autoridad_id>")
def list_autoridad_listas_de_acuerdos(autoridad_id):
    """Listado de Listas de Acuerdos activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_activas, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_listas_de_acuerdos_inactive(autoridad_id):
    """Listado de Listas de Acuerdos inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_inactivas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "B").order_by(ListaDeAcuerdo.creado.desc()).limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_inactivas, estatus="B")


@listas_de_acuerdos.route("/listas_de_acuerdos/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
@permission_required(Permiso.CREAR_ADMINISTRATIVOS)
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
    return render_template("listas_de_acuerdos/detail.jinja2", lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos.route("/listas_de_acuerdos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Lista de Acuerdos"""
    form_search = ListaDeAcuerdoSearchForm()
    if form_search.validate_on_submit():
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha <= form_search.fecha_hasta.data)
        consulta = consulta.order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("listas_de_acuerdos/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Subir Lista de Acuerdos como juzgado"""

    # Para validar la fecha
    dias_limite = 7
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-dias_limite)

    # Validar autoridad
    autoridad = current_user.autoridad
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para listas de acuerdos.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = unidecode(form.descripcion.data.strip())
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
                raise ListaDeAcuerdoException(f"La fecha no debe ser del futuro ni anterior a {dias_limite} días.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise ListaDeAcuerdoException("No es un archivo PDF.")
        except ListaDeAcuerdoException as error:
            flash(str(error), "warning")
            form.fecha.data = hoy
            return render_template("listas_de_acuerdos/new.jinja2", form=form)

        # TODO Si existe una lista de acuerdos de la misma fecha, dar de baja la antigua

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        archivo_str = f"{fecha_str}-lista-de-acuerdos-{lista_de_acuerdo.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        lista_de_acuerdo.archivo = archivo_str
        lista_de_acuerdo.url = url
        lista_de_acuerdo.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "LISTA DE ACUERDOS"
    form.fecha.data = hoy
    return render_template("listas_de_acuerdos/new.jinja2", form=form)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Lista de Acuerdos para una autoridad dada"""

    # Para validar la fecha
    dias_limite = 30
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-dias_limite)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para listas de acuerdos.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = unidecode(form.descripcion.data.strip())
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
                raise ListaDeAcuerdoException(f"La fecha no debe ser del futuro ni anterior a {dias_limite} días.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise ListaDeAcuerdoException("No es un archivo PDF.")
        except ListaDeAcuerdoException as error:
            flash(str(error), "warning")
            form.fecha.data = hoy
            return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # TODO Si existe una lista de acuerdos de la misma fecha, dar de baja la antigua

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        archivo_str = f"{fecha_str}-lista-de-acuerdos-{lista_de_acuerdo.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        lista_de_acuerdo.archivo = archivo_str
        lista_de_acuerdo.url = url
        lista_de_acuerdo.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "LISTA DE ACUERDOS"
    form.fecha.data = hoy
    return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


@listas_de_acuerdos.route("/listas_de_acuerdos/edicion/<int:lista_de_acuerdo_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(lista_de_acuerdo_id):
    """Editar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    form = ListaDeAcuerdoEditForm()
    if form.validate_on_submit():
        lista_de_acuerdo.fecha = form.fecha.data
        lista_de_acuerdo.descripcion = form.descripcion.data
        lista_de_acuerdo.save()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))
    form.fecha.data = lista_de_acuerdo.fecha
    form.descripcion.data = lista_de_acuerdo.descripcion
    return render_template("listas_de_acuerdos/edit.jinja2", form=form, lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos.route("/listas_de_acuerdos/eliminar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(lista_de_acuerdo_id):
    """Eliminar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "A":
        if current_user.can_admin("listas_de_acuerdos") or (current_user.autoridad_id == lista_de_acuerdo.autoridad_id):
            lista_de_acuerdo.delete()
            flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} eliminado.", "success")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


@listas_de_acuerdos.route("/listas_de_acuerdos/recuperar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(lista_de_acuerdo_id):
    """Recuperar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "B":
        if current_user.can_admin("listas_de_acuerdos") or (current_user.autoridad_id == lista_de_acuerdo.autoridad_id):
            lista_de_acuerdo.recover()
            flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} recuperado.", "success")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo=lista_de_acuerdo))
