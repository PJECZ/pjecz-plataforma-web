"""
CITAS Clientes, vistas
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.pwgen import generar_contrasena
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, TOKEN_REGEXP, safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_clientes.models import CITCliente

from plataforma_web.blueprints.cit_clientes.forms import CITClientesForm

MODULO = "CIT CLIENTES"
RENOVACION_CONTRASENA_DIAS = 360

cit_clientes = Blueprint("cit_clientes", __name__, template_folder="templates")


@cit_clientes.route("/cit_clientes")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Cliente activos"""
    activos = CITCliente.query.filter(CITCliente.estatus == "A").all()
    return render_template(
        "cit_clientes/list.jinja2",
        clientes=activos,
        titulo="Clientes",
        estatus="A",
    )


@cit_clientes.route("/cit_clientes/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Cliente inactivos"""
    inactivos = CITCliente.query.filter(CITCliente.estatus == "B").all()
    return render_template(
        "cit_clientes/list.jinja2",
        clientes=inactivos,
        titulo="Clientes inactivos",
        estatus="B",
    )


@cit_clientes.route("/cit_clientes/<int:cliente_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(cliente_id):
    """Detalle de un Cliente"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    return render_template("cit_clientes/detail.jinja2", cliente=cliente)
