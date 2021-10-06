"""
Autoridades, vistas
"""
from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades.forms import AutoridadForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "AUTORIDADES"

autoridades = Blueprint("autoridades", __name__, template_folder="templates")


@autoridades.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades.route("/autoridades")
def list_active():
    """Listado de Autoridades activos"""
    return render_template(
        "autoridades/list.jinja2",
        autoridades=Autoridad.query.filter(Autoridad.estatus == "A").all(),
        titulo="Autoridades",
        estatus="A",
    )


@autoridades.route("/autoridades/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades inactivos"""
    return render_template(
        "autoridades/list.jinja2",
        autoridades=Autoridad.query.filter(Autoridad.estatus == "B").all(),
        titulo="Autoridades inactivas",
        estatus="B",
    )


@autoridades.route("/autoridades/<int:autoridad_id>")
def detail(autoridad_id):
    """Detalle de un Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    return render_template("autoridades/detail.jinja2", autoridad=autoridad)


@autoridades.route("/autoridades/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Autoridad"""
    form = AutoridadForm()
    if form.validate_on_submit():
        autoridad = Autoridad(
            distrito=form.distrito.data,
            descripcion=form.descripcion.data,
            descripcion_corta=form.descripcion_corta.data,
            clave=form.clave.data,
            es_jurisdiccional=form.es_jurisdiccional.data == 1,
        )
        autoridad.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("autoridades/new.jinja2", form=form)


@autoridades.route("/autoridades/edicion/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(autoridad_id):
    """Editar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadForm()
    if form.validate_on_submit():
        autoridad.distrito = form.distrito.data
        autoridad.descripcion = form.descripcion.data
        autoridad.descripcion_corta = form.descripcion_corta.data
        autoridad.clave = form.clave.data
        autoridad.es_jurisdiccional = form.es_jurisdiccional.data
        autoridad.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito
    form.descripcion.data = autoridad.descripcion
    form.descripcion_corta.data = autoridad.descripcion_corta
    form.clave.data = autoridad.clave
    if autoridad.es_jurisdiccional:
        form.es_jurisdiccional.data = 1
    return render_template("autoridades/edit.jinja2", form=form, autoridad=autoridad)


@autoridades.route("/autoridades/eliminar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(autoridad_id):
    """Eliminar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "A":
        autoridad.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))


@autoridades.route("/autoridades/recuperar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(autoridad_id):
    """Recuperar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "B":
        autoridad.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
