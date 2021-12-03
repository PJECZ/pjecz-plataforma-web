"""
Epocas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.epocas.models import Epoca
from plataforma_web.blueprints.epocas.forms import EpocaForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "EPOCAS"

epocas = Blueprint("epocas", __name__, template_folder="templates")


@epocas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@epocas.route("/epocas")
def list_active():
    """Listado de Epocas activas"""
    epocas_activas = Epoca.query.filter(Epoca.estatus == "A").all()
    return render_template(
        "epocas/list.jinja2",
        epocas=epocas_activas,
        titulo="Épocas",
        estatus="A",
    )


@epocas.route("/epocas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Epocas inactivas"""
    epocas_inactivas = Epoca.query.filter(Epoca.estatus == "B").all()
    return render_template(
        "epocas/list.jinja2",
        epocas=epocas_inactivas,
        titulo="Épocas inactivas",
        estatus="B",
    )


@epocas.route("/epocas/<int:epoca_id>")
def detail(epoca_id):
    """Detalle de una Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    return render_template("epocas/detail.jinja2", epoca=epoca)


@epocas.route("/epocas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Epoca"""
    form = EpocaForm()
    if form.validate_on_submit():
        epoca = Epoca(nombre=safe_string(form.nombre.data))
        epoca.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("epocas/new.jinja2", form=form)


@epocas.route("/epocas/edicion/<int:epoca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(epoca_id):
    """Editar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    form = EpocaForm()
    if form.validate_on_submit():
        epoca.nombre = safe_string(form.nombre.data)
        epoca.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    form.nombre.data = epoca.nombre
    return render_template("epocas/edit.jinja2", form=form, epoca=epoca)


@epocas.route("/epocas/eliminar/<int:epoca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(epoca_id):
    """Eliminar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    if epoca.estatus == "A":
        epoca.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("epocas.detail", epoca_id=epoca.id))


@epocas.route("/epocas/recuperar/<int:epoca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(epoca_id):
    """Recuperar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    if epoca.estatus == "B":
        epoca.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("epocas.detail", epoca_id=epoca.id))
