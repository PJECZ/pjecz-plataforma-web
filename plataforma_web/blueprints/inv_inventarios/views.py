"""
Inventarios, vistas
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

MODULO = "INV INVENTARIOS"

inv_inventarios = Blueprint("inv_inventarios", __name__, template_folder="templates")


@inv_inventarios.route("/inv_inventarios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Inventarios activos"""
    activos = None  # Clase.query.filter(Clase.estatus == 'A').all()
    return render_template(
        "inv_inventarios/list.jinja2",
        inventarios=activos,
        titulo="Inventarios",
        estatus="A",
    )
