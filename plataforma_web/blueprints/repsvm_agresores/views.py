"""
REPSVM Agresores, vistas
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
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor

MODULO = "REPSVM AGRESORES"

repsvm_agresores = Blueprint("repsvm_agresores", __name__, template_folder="templates")


@repsvm_agresores.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_agresores.route("/repsvm_agresores")
def list_active():
    """Listado de Agresores activos"""
    repsvm_agresores_activos = REPSVMAgresor.query.filter(REPSVMAgresor.estatus == "A").all()
    return render_template(
        "repsvm_agresores/list.jinja2",
        repsvm_agresores=repsvm_agresores_activos,
        titulo="Agresores",
        estatus="A",
    )


@repsvm_agresores.route("/repsvm_agresores/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Agresores inactivos"""
    repsvm_agresores_inactivos = REPSVMAgresor.query.filter(REPSVMAgresor.estatus == "B").all()
    return render_template(
        "repsvm_agresores/list.jinja2",
        repsvm_agresores=repsvm_agresores_inactivos,
        titulo="Agresores inactivos",
        estatus="B",
    )


@repsvm_agresores.route("/repsvm_agresores/<int:repsvm_agresor_id>")
def detail(repsvm_agresor_id):
    """Detalle de un Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    return render_template("repsvm_agresores/detail.jinja2", repsvm_agresor=repsvm_agresor)
