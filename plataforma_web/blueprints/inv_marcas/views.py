"""
Modelos, vistas
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
from plataforma_web.blueprints.inv_marcas.models import INVMarcas

MODULO = "INV MARCAS"

inv_marcas = Blueprint("inv_marcas", __name__, template_folder="templates")


@inv_marcas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_marcas.route("/inv_marcas")
def list_active():
    """Listado de Marcas activos"""
    marcas_activos = INVMarcas.query.filter(INVMarcas.estatus == "A").all()
    return render_template(
        "inv_marcas/list.jinja2",
        modelo=marcas_activos,
        titulo="Marcas",
        estatus="A",
    )


@inv_marcas.route("/inv_marcas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Marcas inactivos"""
    marcas_inactivos = INVMarcas.query.filter(INVMarcas.estatus == "B").all()
    return render_template(
        "inv_marcas/list.jinja2",
        modelos=marcas_inactivos,
        titulo="Marcas inactivos",
        estatus="B",
    )


@inv_marcas.route("/inv_marcas/<int:marca_id>")
def detail(marca_id):
    """Detalle de un Marcas"""
    marca = INVMarcas.query.get_or_404(marca_id)
    return render_template("inv_marcas/detail.jinja2", marca=marca)
