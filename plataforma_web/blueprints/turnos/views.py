"""
Turnos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib import datatables
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.turnos.models import Turno

MODULO = "TURNOS"

turnos = Blueprint("turnos", __name__, template_folder="templates")


@turnos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@turnos.route("/turnos")
def list_active():
    """Listado de Turnos activos"""
    return render_template(
        "turnos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Turnos",
        estatus="A",
    )


@turnos.route("/turnos/<int:turno_id>")
def detail(turno_id):
    """Detalle de un Turno"""
    turno = Turno.query.get_or_404(turno_id)
    return render_template("turnos/detail.jinja2", turno=turno)
