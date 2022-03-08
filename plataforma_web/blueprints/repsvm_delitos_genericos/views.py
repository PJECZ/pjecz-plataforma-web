"""
REPSVM Delitos Genericos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.repsvm_delitos_genericos.models import REPSVMDelitoGenerico
from plataforma_web.blueprints.repsvm_delitos_genericos.forms import REPSVMDelitoGenericoForm

MODULO = "REPSVM DELITOS GENERICOS"

repsvm_delitos_genericos = Blueprint("repsvm_delitos_genericos", __name__, template_folder="templates")


@repsvm_delitos_genericos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos")
def list_active():
    """Listado de Delitos Genericos activos"""
    repsvm_delitos_genericos_activos = REPSVMDelitoGenerico.query.filter(REPSVMDelitoGenerico.estatus == "A").all()
    return render_template(
        "repsvm_delitos_genericos/list.jinja2",
        repsvm_delitos_genericos=repsvm_delitos_genericos_activos,
        titulo="Delitos Genericos",
        estatus="A",
    )


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Delitos Genericos inactivos"""
    repsvm_delitos_genericos_inactivos = REPSVMDelitoGenerico.query.filter(REPSVMDelitoGenerico.estatus == "B").all()
    return render_template(
        "repsvm_delitos_genericos/list.jinja2",
        repsvm_delitos_genericos=repsvm_delitos_genericos_inactivos,
        titulo="Delitos Genericos inactivos",
        estatus="B",
    )


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/<int:repsvm_delito_generico_id>")
def detail(repsvm_delito_generico_id):
    """Detalle de un Delito Generico"""
    repsvm_delito_generico = REPSVMDelitoGenerico.query.get_or_404(repsvm_delito_generico_id)
    return render_template("repsvm_delitos_genericos/detail.jinja2", repsvm_delito_generico=repsvm_delito_generico)


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Delito Generico"""
    form = REPSVMDelitoGenericoForm()
    if form.validate_on_submit():
        repsvm_delito_generico = REPSVMDelitoGenerico(nombre=safe_string(form.nombre.data))
        repsvm_delito_generico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Delito Generico {repsvm_delito_generico.nombre}"),
            url=url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("repsvm_delitos_genericos/new.jinja2", form=form)


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/edicion/<int:repsvm_delito_generico_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_delito_generico_id):
    """Editar Delito Generico"""
    repsvm_delito_generico = REPSVMDelitoGenerico.query.get_or_404(repsvm_delito_generico_id)
    form = REPSVMDelitoGenericoForm()
    if form.validate_on_submit():
        repsvm_delito_generico.nombre = safe_string(form.nombre.data)
        repsvm_delito_generico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Delito Generico {repsvm_delito_generico.nombre}"),
            url=url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = repsvm_delito_generico.nombre
    return render_template("repsvm_delitos_genericos/edit.jinja2", form=form, repsvm_delito_generico=repsvm_delito_generico)


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/eliminar/<int:repsvm_delito_generico_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(repsvm_delito_generico_id):
    """Eliminar Delito Generico"""
    repsvm_delito_generico = REPSVMDelitoGenerico.query.get_or_404(repsvm_delito_generico_id)
    if repsvm_delito_generico.estatus == "A":
        repsvm_delito_generico.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Delito Generico {repsvm_delito_generico.nombre}"),
            url=url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id))


@repsvm_delitos_genericos.route("/repsvm_delitos_genericos/recuperar/<int:repsvm_delito_generico_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(repsvm_delito_generico_id):
    """Recuperar Delito Generico"""
    repsvm_delito_generico = REPSVMDelitoGenerico.query.get_or_404(repsvm_delito_generico_id)
    if repsvm_delito_generico.estatus == "B":
        repsvm_delito_generico.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Delito Generico {repsvm_delito_generico.nombre}"),
            url=url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_delitos_genericos.detail", repsvm_delito_generico_id=repsvm_delito_generico.id))
