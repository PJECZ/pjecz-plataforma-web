"""
REPSVM Delitos Especificos, vistas
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
from plataforma_web.blueprints.repsvm_delitos_especificos.models import REPSVMDelitoEspecifico
from plataforma_web.blueprints.repsvm_delitos_especificos.forms import REPSVMDelitoEspecificoForm

MODULO = "REPSVM DELITOS ESPECIFICOS"

repsvm_delitos_especificos = Blueprint("repsvm_delitos_especificos", __name__, template_folder="templates")


@repsvm_delitos_especificos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos")
def list_active():
    """Listado de Delitos Especificos activos"""
    repsvm_delitos_especificos_activos = REPSVMDelitoEspecifico.query.filter(REPSVMDelitoEspecifico.estatus == "A").all()
    return render_template(
        "repsvm_delitos_especificos/list.jinja2",
        repsvm_delitos_especificos=repsvm_delitos_especificos_activos,
        titulo="Delitos Especificos",
        estatus="A",
    )


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Delitos Especificos inactivos"""
    repsvm_delitos_especificos_inactivos = REPSVMDelitoEspecifico.query.filter(REPSVMDelitoEspecifico.estatus == "B").all()
    return render_template(
        "repsvm_delitos_especificos/list.jinja2",
        repsvm_delitos_especificos=repsvm_delitos_especificos_inactivos,
        titulo="Delitos Especificos inactivos",
        estatus="B",
    )


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/<int:repsvm_delito_especifico_id>")
def detail(repsvm_delito_especifico_id):
    """Detalle de un Delito Especifico"""
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    return render_template("repsvm_delitos_especificos/detail.jinja2", repsvm_delito_especifico=repsvm_delito_especifico)


@repsvm_delitos_especificos.route('/repsvm_delitos_especificos/nuevo', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """ Nuevo DelitoEspecifico """
    form = REPSVMDelitoEspecificoForm()
    if form.validate_on_submit():
        repsvm_delito_especifico = REPSVMDelitoEspecifico(descripcion=safe_string(form.descripcion.data))
        repsvm_delito_especifico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo DelitoEspecifico {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template('repsvm_delitos_especificos/new.jinja2', form=form)


@repsvm_delitos_especificos.route('/repsvm_delitos_especificos/edicion/<int:repsvm_delito_especifico_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_delito_especifico_id):
    """ Editar Delito Especifico """
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    form = REPSVMDelitoEspecificoForm()
    if form.validate_on_submit():
        repsvm_delito_especifico.descripcion = safe_string(form.descripcion.data)
        repsvm_delito_especifico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Delito Especifico {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.descripcion.data = repsvm_delito_especifico.descripcion
    return render_template('repsvm_delitos_especificos/edit.jinja2', form=form, repsvm_delito_especifico=repsvm_delito_especifico)
