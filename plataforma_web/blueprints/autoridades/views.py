"""
Autoridades, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades.forms import AutoridadNewForm, AutoridadEditForm, AutoridadSearchForm
from plataforma_web.blueprints.usuarios.models import Usuario

autoridades = Blueprint("autoridades", __name__, template_folder="templates")


@autoridades.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """ Permiso por defecto """


@autoridades.route("/autoridades")
def list_active():
    """ Listado de Autoridades """
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == "A").all()
    return render_template("autoridades/list.jinja2", autoridades=autoridades_activas, estatus="A")


@autoridades.route("/autoridades/inactivas")
def list_inactive():
    """ Listado de Autoridades inactivas """
    autoridades_inactivas = Autoridad.query.filter(Autoridad.estatus == "B").all()
    return render_template("autoridades/list.jinja2", autoridades=autoridades_inactivas, estatus="B")


@autoridades.route("/autoridades/<int:autoridad_id>")
def detail(autoridad_id):
    """ Detalle de una Autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    usuarios = Usuario.query.filter(Usuario.autoridad == autoridad).filter(Usuario.estatus == "A").all()
    return render_template("autoridades/detail.jinja2", autoridad=autoridad, usuarios=usuarios)


@autoridades.route("/autoridades/buscar", methods=["GET", "POST"])
def search():
    """ Buscar Autoridades """
    form_search = AutoridadSearchForm()
    if form_search.validate_on_submit():
        descripcion = form_search.descripcion.data
        consulta = Autoridad.query.filter(Autoridad.descripcion.ilike(f"%{descripcion}%"))
        consulta = consulta.order_by(Autoridad.descripcion).limit(100).all()
        return render_template("autoridades/list.jinja2", autoridades=consulta)
    return render_template("autoridades/search.jinja2", form=form_search)


@autoridades.route("/autoridades/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CATALOGOS)
def new():
    """ Nueva Autoridad """
    form = AutoridadNewForm()
    if form.validate_on_submit():
        distrito = form.distrito.data
        directorio = f"{distrito.nombre}/{form.descripcion.data}"
        autoridad = Autoridad(
            distrito=distrito,
            descripcion=form.descripcion.data,
            clave=form.clave.data.upper(),
            directorio_listas_de_acuerdos=directorio,
            directorio_sentencias=directorio,
            es_jurisdiccional=form.es_jurisdiccional.data,
        )
        autoridad.save()
        flash(f"Autoridad {autoridad.descripcion} guardado.", "success")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    return render_template("autoridades/new.jinja2", form=form)


@autoridades.route("/autoridades/edicion/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def edit(autoridad_id):
    """ Editar Autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadEditForm()
    if form.validate_on_submit():
        autoridad.distrito = form.distrito.data
        autoridad.descripcion = form.descripcion.data
        autoridad.clave = form.clave.data
        autoridad.directorio_listas_de_acuerdos = form.directorio_listas_de_acuerdos.data
        autoridad.directorio_sentencias = form.directorio_sentencias.data
        autoridad.es_jurisdiccional = form.es_jurisdiccional.data
        autoridad.save()
        flash(f"Autoridad {autoridad.descripcion} guardado.", "success")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    form.distrito.data = autoridad.distrito
    form.descripcion.data = autoridad.descripcion
    form.clave.data = autoridad.clave
    form.directorio_listas_de_acuerdos.data = autoridad.directorio_listas_de_acuerdos
    form.directorio_sentencias.data = autoridad.directorio_sentencias
    form.es_jurisdiccional.data = autoridad.es_jurisdiccional
    return render_template("autoridades/edit.jinja2", form=form, autoridad=autoridad)


@autoridades.route("/autoridades/eliminar/<int:autoridad_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(autoridad_id):
    """ Eliminar Autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "A":
        autoridad.delete()
        flash(f"Autoridad {autoridad.descripcion} eliminado.", "success")
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad_id))


@autoridades.route("/autoridades/recuperar/<int:autoridad_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(autoridad_id):
    """ Recuperar Autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "B":
        autoridad.recover()
        flash(f"Autoridad {autoridad.descripcion} recuperado.", "success")
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad_id))
