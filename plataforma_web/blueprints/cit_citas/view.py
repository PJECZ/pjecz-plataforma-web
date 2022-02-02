"""
CITAS, vistas
"""

from datetime import date, datetime
import json

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib import datatables

from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
#from plataforma_web.blueprints.cit_clientes.models import CITCliente

#from plataforma_web.blueprints.cit_clientes.forms import CITClienteSearchForm

MODULO = "CIT CITAS"

cit_citas = Blueprint("cit_citas", __name__, template_folder="templates")


@cit_citas.route("/cit_citas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Citas activas"""
    activos = None# CITCliente.query.filter(CITCliente.estatus == "A").all()
    return render_template(
        "cit_citas/list.jinja2",
        citas=activos,
        titulo="Citas",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )
