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

MODULO = "REPSVM"

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
