"""
Peritos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.peritos.forms import PeritoForm

peritos = Blueprint("peritos", __name__, template_folder="templates")


@peritos.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    """ Permiso por defecto """


@peritos.route("/peritos")
def list_active():
    """ Listado de Peritos """
    peritos_activos = Perito.query.filter(Perito.estatus == "A").all()
    return render_template("peritos/list.jinja2", peritos=peritos_activos)


@peritos.route("/peritos/<int:perito_id>")
def detail(perito_id):
    """ Detalle de un Perito """
    perito = Perito.query.get_or_404(perito_id)
    return render_template("peritos/detail.jinja2", perito=perito)


@peritos.route("/peritos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONTENIDOS)
def new():
    """ Nuevo Perito """
    form = PeritoForm()
    if form.validate_on_submit():
        perito = Perito(
            distrito=form.distrito.data,
            tipo=form.tipo.data,
            nombre=form.nombre.data,
            domicilio=form.domicilio.data,
            telefono_fijo=form.telefono_fijo.data,
            telefono_celular=form.telefono_celular.data,
            email=form.email.data,
            notas=form.notas.data,
        )
        perito.save()
        flash(f"Perito {perito.nombre} guardado.", "success")
        return redirect(url_for("peritos.list_active"))
    return render_template("peritos/new.jinja2", form=form)


@peritos.route("/peritos/edicion/<int:perito_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def edit(perito_id):
    """ Editar Perito """
    perito = Perito.query.get_or_404(perito_id)
    form = PeritoForm()
    if form.validate_on_submit():
        perito.distrito = form.distrito.data
        perito.tipo = form.tipo.data
        perito.nombre = form.nombre.data
        perito.domicilio = form.domicilio.data
        perito.telefono_fijo = form.telefono_fijo.data
        perito.telefono_celular = form.telefono_celular.data
        perito.email = form.email.data
        perito.notas = form.notas.data
        perito.save()
        flash(f"Perito {perito.nombre} guardado.", "success")
        return redirect(url_for("peritos.detail", perito_id=perito.id))
    form.distrito.data = perito.distrito
    form.tipo.data = perito.tipo
    form.nombre.data = perito.nombre
    form.domicilio.data = perito.domicilio
    form.telefono_fijo.data = perito.telefono_fijo
    form.telefono_celular.data = perito.telefono_celular
    form.email.data = perito.email
    form.notas.data = perito.notas
    return render_template("peritos/edit.jinja2", form=form, perito=perito)


@peritos.route("/peritos/eliminar/<int:perito_id>")
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def delete(perito_id):
    """ Eliminar Perito """
    perito = Perito.query.get_or_404(perito_id)
    if perito.estatus == "A":
        perito.delete()
        flash(f"Perito {perito.nombre} eliminado.", "success")
    return redirect(url_for("peritos.detail", perito_id=perito_id))


@peritos.route("/peritos/recuperar/<int:perito_id>")
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def recover(perito_id):
    """ Recuperar Perito """
    perito = Perito.query.get_or_404(perito_id)
    if perito.estatus == "B":
        perito.recover()
        flash(f"Perito {perito.nombre} recuperado.", "success")
    return redirect(url_for("peritos.detail", perito_id=perito_id))
