"""
Glosas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.glosas.models import Glosa
from plataforma_web.blueprints.glosas.forms import GlosaForm

glosas = Blueprint("glosas", __name__, template_folder="templates")


@glosas.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    """ Permiso por defecto """


@glosas.route("/glosas")
def list_active():
    """ Listado de Glosas """
    glosas_activos = Glosa.query.filter(Glosa.estatus == "A").limit(100).all()
    return render_template("glosas/list.jinja2", glosas=glosas_activos)


@glosas.route("/glosas/<int:glosa_id>")
def detail(glosa_id):
    """ Detalle de un Glosa """
    glosa = Glosa.query.get_or_404(glosa_id)
    return render_template("glosas/detail.jinja2", glosa=glosa)


@glosas.route("/glosas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONTENIDOS)
def new():
    """ Nuevo Glosa """
    form = GlosaForm()
    if form.validate_on_submit():
        glosa = Glosa(
            autoridad=form.autoridad.data,
            fecha=form.fecha.data,
            juicio_tipo=form.juicio_tipo.data,
            expediente=form.expediente.data,
            url=form.url.data,
        )
        glosa.save()
        flash(f"Glosa {glosa.expediente} guardado.", "success")
        return redirect(url_for("glosas.detail", glosa_id=glosa.id))
    return render_template("glosas/new.jinja2", form=form)


@glosas.route("/glosas/edicion/<int:glosa_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def edit(glosa_id):
    """ Editar Glosa """
    glosa = Glosa.query.get_or_404(glosa_id)
    form = GlosaForm()
    if form.validate_on_submit():
        glosa.autoridad = form.autoridad.data
        glosa.fecha = form.fecha.data
        glosa.juicio_tipo = form.juicio_tipo.data
        glosa.expediente = form.expediente.data
        glosa.url = form.url.data
        glosa.save()
        flash(f"Glosa {glosa.nombre} guardado.", "success")
        return redirect(url_for("glosas.detail", glosa_id=glosa.id))
    form.autoridad.data = glosa.autoridad
    form.fecha.data = glosa.fecha
    form.juicio_tipo.data = glosa.juicio_tipo
    form.expediente.data = glosa.expediente
    form.url.data = glosa.url
    return render_template("glosas/edit.jinja2", form=form, glosa=glosa)
