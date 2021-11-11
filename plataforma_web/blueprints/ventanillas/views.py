"""
Ventanillas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from lib import datatables
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.ventanillas.models import Ventanilla

MODULO = "VENTANILLAS"

ventanillas = Blueprint("ventanillas", __name__, template_folder="templates")


@ventanillas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ventanillas.route("/ventanillas")
def list_active():
    """Listado de Ventanillas activas"""
    ventanillas_activas = Ventanilla.query.filter(Ventanilla.estatus == "A").all()
    return render_template(
        "ventanillas/list.jinja2",
        ventanillas=ventanillas_activas,
        titulo="Ventanillas",
        estatus="A",
    )


@ventanillas.route("/ventanillas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Ventanillas inactivas"""
    ventanillas_inactivas = Ventanilla.query.filter(Ventanilla.estatus == "B").all()
    return render_template(
        "ventanillas/list.jinja2",
        ventanillas=ventanillas_inactivas,
        titulo="Ventanillas inactivos",
        estatus="B",
    )


@ventanillas.route("/ventanillas/<int:ventanilla_id>")
def detail(ventanilla_id):
    """Detalle de una Ventanilla"""
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    return render_template("ventanillas/detail.jinja2", ventanilla=ventanilla)
