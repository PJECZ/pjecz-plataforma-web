"""
Modulos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.modulos.models import Modulo

modulos = Blueprint("modulos", __name__, template_folder="templates")


@modulos.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@modulos.route("/modulos")
def list_active():
    """Listado de Modulos activos"""
    modulos_activos = Modulo.query.filter(Modulo.estatus == "A").order_by(Modulo.nombre).all()
    return render_template("modulos/list.jinja2", modulos=modulos_activos, estatus="A")


@modulos.route("/modulos/inactivos")
@permission_required(Permiso.MODIFICAR_)
def list_inactive():
    """Listado de Modulos inactivos"""
    modulos_inactivos = Modulo.query.filter(Modulo.estatus == "B").order_by(Modulo.nombre).all()
    return render_template("modulos/list.jinja2", modulos=modulos_inactivos, estatus="B")
