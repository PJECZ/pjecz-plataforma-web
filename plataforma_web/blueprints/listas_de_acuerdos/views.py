"""
Listas de Acuerdos, vistas
"""
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
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
def list_active():
    """ Listado de Listas de Acuerdos """
    listas_de_acuerdos_activos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", listas_de_acuerdos=listas_de_acuerdos_activos)


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
    """ Nuevo Lista de Acuerdos """
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        # Definir ruta /listas de acuerdo/distrito/autoridad/año/mes/YYYY-MM-DD-lista-de-acuerdos.pdf
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        fecha = form.fecha.data
        fecha_str = fecha.strftime("%Y-%m-%d")
        ruta = Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, fecha.year, fecha.month, f"{fecha_str}-lista-de-acuerdos.pdf")
        # Subir archivo a Google Storage
        archivo = request.files["archivo"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(DEPOSITO)
        blob = bucket.blob(str(ruta))
        blob.upload_from_string(archivo.stream.read())
        # Insertar en la base de datos
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
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
