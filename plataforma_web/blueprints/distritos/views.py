"""
Distritos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.forms import DistritoForm

distritos = Blueprint("distritos", __name__, template_folder="templates")


@distritos.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """ Permiso por defecto """


@distritos.route("/distritos")
def list_active():
    """ Listado de Distritos """
    distritos_activos = Distrito.query.filter(Distrito.estatus == "A").all()
    return render_template("distritos/list.jinja2", distritos=distritos_activos)


@distritos.route("/distritos/<int:distrito_id>")
def detail(distrito_id):
    """ Detalle de un Distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.estatus == "A").all()
    return render_template("distritos/detail.jinja2", distrito=distrito, autoridades=autoridades)


@distritos.route("/distritos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CATALOGOS)
def new():
    """ Nuevo Distrito """
    form = DistritoForm()
    if form.validate_on_submit():
        distrito = Distrito(nombre=form.nombre.data)
        distrito.save()
        flash(f"Distrito {distrito.nombre} guardado.", "success")
        return redirect(url_for("distritos.list_active"))
    return render_template("distritos/new.jinja2", form=form)


@distritos.route("/distritos/edicion/<int:distrito_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def edit(distrito_id):
    """ Editar Distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    form = DistritoForm()
    if form.validate_on_submit():
        distrito.nombre = form.nombre.data
        distrito.save()
        flash(f"Distrito {distrito.nombre} guardado.", "success")
        return redirect(url_for("distritos.detail", distrito_id=distrito.id))
    form.nombre.data = distrito.nombre
    return render_template("distritos/edit.jinja2", form=form, distrito=distrito)


@distritos.route("/distritos/eliminar/<int:distrito_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(distrito_id):
    """ Eliminar Distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "A":
        distrito.delete()
        flash(f"Distrito {distrito.nombre} eliminado.", "success")
    return redirect(url_for("distritos.detail", distrito_id=distrito_id))


@distritos.route("/distritos/recuperar/<int:distrito_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(distrito_id):
    """ Recuperar Distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "B":
        distrito.recover()
        flash(f"Distrito {distrito.nombre} recuperado.", "success")
    return redirect(url_for("distritos.detail", distrito_id=distrito_id))
