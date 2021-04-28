"""
Listas de Acuerdos, vistas
"""
from datetime import date, timedelta
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.listas_de_acuerdos.forms import ListaDeAcuerdoNewForm, ListaDeAcuerdoEditForm, ListaDeAcuerdoSearchForm

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

# DEPOSITO = current_app.config["CLOUD_STORAGE_DEPOSITO"]
DEPOSITO = "pjecz-pruebas"
SUBDIRECTORIO = "Listas de Acuerdos"
DIAS_LIMITE = 5

listas_de_acuerdos = Blueprint("listas_de_acuerdos", __name__, template_folder="templates")


def subir_archivo(autoridad, fecha, archivo, puede_reemplazar=False):
    """Subir archivo de lista de acuerdos"""
    hoy = date.today()
    # Validar autoridad
    if not isinstance(autoridad, Autoridad):
        raise ValueError("El juzgado no es del tipo correcto.")
    if not autoridad.distrito.es_distrito_judicial:
        raise ValueError("El juzgado no está en un distrito jurisdiccional.")
    if not autoridad.es_jurisdiccional:
        raise ValueError("El juzgado no es jurisdiccional.")
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        raise ValueError("El juzgado no tiene directorio para listas de acuerdos.")
    # Validar fecha
    if not isinstance(fecha, date):
        raise ValueError("La fecha no es del tipo correcto.")
    if fecha > hoy:
        raise ValueError("La fecha no debe ser del futuro.")
    if fecha < hoy - timedelta(days=DIAS_LIMITE):
        raise ValueError(f"La fecha no debe ser más antigua a {DIAS_LIMITE} días.")
    # Validar que el archivo sea PDF
    archivo_nombre = secure_filename(archivo.filename.lower())
    if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
        raise ValueError("No es un archivo PDF.")
    lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.fecha == fecha).filter(ListaDeAcuerdo.estatus == "A").first()
    # Si puede reemplazar
    if puede_reemplazar and lista_de_acuerdo is not None:
        raise ValueError("Ya existe una lista de acuerdo con esa fecha. Si va a reemplazar, primero debe eliminarlo.")
    # Si NO puede reemplazar
    if puede_reemplazar is False and fecha != hoy:
        raise ValueError("No puede subir archivos que no sean de hoy.")
    # Definir ruta /SUBDIRECTORIO/DISTRITO/AUTORIDAD/YYYY/MM/YYYY-MM-DD-lista-de-acuerdos.pdf
    ano_str = fecha.strftime("%Y")
    mes_str = fecha.strftime("%m")
    archivo_str = fecha.strftime("%Y-%m-%d") + "-lista-de-acuerdos.pdf"
    ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))
    # Subir archivo a Google Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(DEPOSITO)
    blob = bucket.blob(ruta_str)
    blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
    return (archivo_str, blob.public_url)


@listas_de_acuerdos.route("/listas_de_acuerdos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(ListaDeAcuerdo.decode_id(id_hashed))
    return render_template("listas_de_acuerdos/checkout.jinja2", lista_de_acuerdo=lista_de_acuerdo)


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
    # Si su autoridad es jurisdiccional
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
    """Listado de Autoridades de un Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.descripcion).all()
    return render_template("listas_de_acuerdos/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/autoridad/<int:autoridad_id>")
def list_autoridad_listas_de_acuerdos(autoridad_id):
    """Listado de Listas de Acuerdos activas de una Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_activas, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_listas_de_acuerdos_inactive(autoridad_id):
    """Listado de Listas de Acuerdos inactivas de una Autoridad"""
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
        consulta = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == form_search.autoridad.data)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha <= form_search.fecha_hasta.data)
        consulta = consulta.order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=None, listas_de_acuerdos=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("listas_de_acuerdos/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Subir Lista de Acuerdos como juzgado"""
    autoridad = current_user.autoridad
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        fecha = form.fecha.data
        archivo = request.files["archivo"]
        try:
            archivo_str, url = subir_archivo(autoridad, fecha, archivo)
        except ValueError as error:
            flash(error, "error")
            return redirect(url_for("listas_de_acuerdos.new"))
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            archivo=archivo_str,
            descripcion=form.descripcion.data,
            url=url,
        )
        lista_de_acuerdo.save()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))
    # Si ya hay una lista de acuerdo de hoy, mostrar un mensaje que advierta que se va a reemplazar
    hoy = date.today()
    lista_de_hoy = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.fecha == hoy).first()
    if lista_de_hoy is not None:
        flash(f"¡ADVERTENCIA! Ya hay una lista de acuerdos del {hoy}. Si la sube se reemplazará.", "warning")
    # Como juzgados son predefinidos estos campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "Lista de Acuerdos"
    form.fecha.data = hoy
    return render_template("listas_de_acuerdos/new.jinja2", form=form)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Nueva Lista de Acuerdos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        fecha = form.fecha.data
        archivo = request.files["archivo"]
        try:
            archivo_str, url = subir_archivo(autoridad, fecha, archivo, puede_reemplazar=True)
        except ValueError as error:
            flash(error, "error")
            return redirect(url_for("listas_de_acuerdos.new_for_autoridad", autoridad_id=autoridad_id))
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            archivo=archivo_str,
            descripcion=form.descripcion.data,
            url=url,
        )
        lista_de_acuerdo.save()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "Lista de Acuerdos"
    form.fecha.data = date.today()
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
        lista_de_acuerdo.delete()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} eliminado.", "success")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


@listas_de_acuerdos.route("/listas_de_acuerdos/recuperar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(lista_de_acuerdo_id):
    """Recuperar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "B":
        lista_de_acuerdo.recover()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} recuperado.", "success")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo=lista_de_acuerdo))
