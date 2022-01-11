"""
Peritos Tipos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo
from plataforma_web.blueprints.peritos_tipos.forms import PeritoTipoForm

MODULO = "PERITOS TIPOS"

peritos_tipos = Blueprint("peritos_tipos", __name__, template_folder="templates")


@peritos_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@peritos_tipos.route("/peritos_tipos")
def list_active():
    """Listado de Tipos de Peritos activos"""
    peritos_tipos_activos = PeritoTipo.query.filter(PeritoTipo.estatus == "A").all()
    return render_template(
        "peritos_tipos/list.jinja2",
        peritos_tipos=peritos_tipos_activos,
        titulo="Tipos de Peritos",
        estatus="A",
    )


@peritos_tipos.route("/peritos_tipos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Peritos inactivos"""
    peritos_tipos_inactivos = PeritoTipo.query.filter(PeritoTipo.estatus == "B").all()
    return render_template(
        "peritos_tipos/list.jinja2",
        peritos_tipos=peritos_tipos_inactivos,
        titulo="Tipos de Peritos inactivos",
        estatus="B",
    )


@peritos_tipos.route("/peritos_tipos/<int:perito_tipo_id>")
def detail(perito_tipo_id):
    """Detalle de un Tipo de Perito"""
    perito_tipo = PeritoTipo.query.get_or_404(perito_tipo_id)
    return render_template("peritos_tipos/detail.jinja2", perito_tipo=perito_tipo)


@peritos_tipos.route("/peritos_tipos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Tipo de Perito"""
    form = PeritoTipoForm()
    if form.validate_on_submit():
        perito_tipo = PeritoTipo(nombre=safe_string(form.nombre.data))
        perito_tipo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Tipo de Perito {perito_tipo.nombre}"),
            url=url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("peritos_tipos/new.jinja2", form=form)


@peritos_tipos.route("/peritos_tipos/edicion/<int:perito_tipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(perito_tipo_id):
    """Editar Tipo de Perito"""
    perito_tipo = PeritoTipo.query.get_or_404(perito_tipo_id)
    form = PeritoTipoForm()
    if form.validate_on_submit():
        perito_tipo.nombre = safe_string(form.nombre.data)
        perito_tipo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Tipo de Perito {perito_tipo.nombre}"),
            url=url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = perito_tipo.nombre
    return render_template("peritos_tipos/edit.jinja2", form=form, perito_tipo=perito_tipo)


@peritos_tipos.route("/peritos_tipos/eliminar/<int:perito_tipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(perito_tipo_id):
    """Eliminar Tipo de Perito"""
    perito_tipo = PeritoTipo.query.get_or_404(perito_tipo_id)
    if perito_tipo.estatus == "A":
        perito_tipo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Tipo de Perito {perito_tipo.nombre}"),
            url=url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id))


@peritos_tipos.route("/peritos_tipos/recuperar/<int:perito_tipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(perito_tipo_id):
    """Recuperar Tipo de Perito"""
    perito_tipo = PeritoTipo.query.get_or_404(perito_tipo_id)
    if perito_tipo.estatus == "B":
        perito_tipo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Tipo de Perito {perito_tipo.nombre}"),
            url=url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("peritos_tipos.detail", perito_tipo_id=perito_tipo.id))
