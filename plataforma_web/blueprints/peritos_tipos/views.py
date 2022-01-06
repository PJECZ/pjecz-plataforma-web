"""
Peritos Tipos, vistas
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
from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo

MODULO = "PERITOS TIPOS"

peritos_tipos = Blueprint("peritos_tipos", __name__, template_folder="templates")


@peritos_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@peritos_tipos.route("/peritos_tipos")
def list_active():
    """Listado de Tipos de Peritos activos"""
    peritos_tipos_activos = PeritoTipo.query.filter(PeritoTipo.estatus == "A").all()
    return render_template(
        "peritos_tipos/list.jinja2",
        peritos_tipos=peritos_tipos_activos,
        titulo="Tipos de Peritos",
        estatus="A",
    )


@peritos_tipos.route("/peritos_tipos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Peritos inactivos"""
    peritos_tipos_inactivos = PeritoTipo.query.filter(PeritoTipo.estatus == "B").all()
    return render_template(
        "peritos_tipos/list.jinja2",
        peritos_tipos=peritos_tipos_inactivos,
        titulo="Tipos de Peritos inactivos",
        estatus="B",
    )


@peritos_tipos.route("/peritos_tipos/<int:perito_tipo_id>")
def detail(perito_tipo_id):
    """Detalle de un Tipo de Perito"""
    perito_tipo = PeritoTipo.query.get_or_404(perito_tipo_id)
    return render_template("peritos_tipos/detail.jinja2", perito_tipo=perito_tipo)
