"""
Listas de Acuerdos, vistas
"""
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.listas_de_acuerdos.forms import ListaDeAcuerdoNewForm, ListaDeAcuerdoEditForm, ListaDeAcuerdoSearchForm
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

DEPOSITO = "conatrib-pjecz-gob-mx"
SUBDIRECTORIO = "Listas de Acuerdos"

listas_de_acuerdos = Blueprint("listas_de_acuerdos", __name__, template_folder="templates")


@listas_de_acuerdos.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    """ Permiso por defecto """


@listas_de_acuerdos.route("/listas_de_acuerdos")
def list_distritos():
    """ Listado de Distritos """
    distritos = Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("listas_de_acuerdos/list_distritos.jinja2", distritos=distritos)


@listas_de_acuerdos.route("/listas_de_acuerdos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """ Listado de Autoridades de un Distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).order_by(Autoridad.descripcion).all()
    return render_template("listas_de_acuerdos/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades)


@listas_de_acuerdos.route("/listas_de_acuerdos/autoridad/<int:autoridad_id>")
def list_active(autoridad_id):
    """ Listado de Listas de Acuerdos activas de una Autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "A").all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_activas)


@listas_de_acuerdos.route("/listas_de_acuerdos/rastrear/<int:autoridad_id>")
def trace(autoridad_id):
    """ Rastrear Listas de Acuerdos """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("listas_de_acuerdos.tasks.rastrear"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="listas_de_acuerdos.tasks.rastrear",
            descripcion=f"Rastrear listas de acuerdos de {autoridad.descripcion} de {autoridad.distrito.nombre}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("listas_de_acuerdos.list_active", autoridad_id=autoridad.id))


@listas_de_acuerdos.route("/listas_de_acuerdos/<int:lista_de_acuerdo_id>")
def detail(lista_de_acuerdo_id):
    """ Detalle de una Lista de Acuerdos """
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    return render_template("listas_de_acuerdos/detail.jinja2", lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos.route("/listas_de_acuerdos/buscar", methods=["GET", "POST"])
def search():
    """ Buscar Lista de Acuerdos """
    form_search = ListaDeAcuerdoSearchForm()  # TODO Programar búsqueda
    distritos = Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("listas_de_acuerdos/search.jinja2", form=form_search, distritos=distritos)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONTENIDOS)
def new():
    """ Nueva Lista de Acuerdos """
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        fecha = form.fecha.data
        # Definir ruta /SUBDIRECTORIO/DISTRITO/AUTORIDAD/YYYY/MM/YYYY-MM-DD-lista-de-acuerdos.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = fecha.strftime("%m")
        archivo_str = fecha.strftime("%Y-%m-%d") + "-lista-de-acuerdos.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))
        # Subir archivo a Google Storage
        archivo = request.files["archivo"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(DEPOSITO)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read())
        # Insertar en la base de datos
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            archivo=archivo_str,
            descripcion=form.descripcion.data,
            url=blob.path,
        )
        lista_de_acuerdo.save()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    distritos = Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("listas_de_acuerdos/new.jinja2", form=form, distritos=distritos)


@listas_de_acuerdos.route("/listas_de_acuerdos/edicion/<int:lista_de_acuerdo_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def edit(lista_de_acuerdo_id):
    """ Editar Lista de Acuerdos """
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
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def delete(lista_de_acuerdo_id):
    """ Eliminar Lista de Acuerdos """
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "A":
        lista_de_acuerdo.delete()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} eliminado.", "success")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


@listas_de_acuerdos.route("/listas_de_acuerdos/recuperar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def recover(lista_de_acuerdo_id):
    """ Recuperar Lista de Acuerdos """
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "B":
        lista_de_acuerdo.recover()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} recuperado.", "success")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo=lista_de_acuerdo))
