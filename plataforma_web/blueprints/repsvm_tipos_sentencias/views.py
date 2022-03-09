"""
REPSVM Tipos de Sentencias, vistas
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
from plataforma_web.blueprints.repsvm_tipos_sentencias.models import REPSVMTipoSentencia

MODULO = "REPSVM TIPOS SENTENCIAS"

repsvm_tipos_sentencias = Blueprint("repsvm_tipos_sentencias", __name__, template_folder="templates")


@repsvm_tipos_sentencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias")
def list_active():
    """Listado de Tipos de Sentencias activos"""
    repsvm_tipos_sentencias_activos = REPSVMTipoSentencia.query.filter(REPSVMTipoSentencia.estatus == "A").all()
    return render_template(
        "repsvm_tipos_sentencias/list.jinja2",
        repsvm_tipos_sentencias=repsvm_tipos_sentencias_activos,
        titulo="Tipos de Sentencias",
        estatus="A",
    )


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Sentencias inactivos"""
    repsvm_tipos_sentencias_inactivos = REPSVMTipoSentencia.query.filter(REPSVMTipoSentencia.estatus == "B").all()
    return render_template(
        "repsvm_tipos_sentencias/list.jinja2",
        repsvm_tipos_sentencias=repsvm_tipos_sentencias_inactivos,
        titulo="Tipos de Sentencias inactivos",
        estatus="B",
    )


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/<int:repsvm_tipo_sentencia_id>")
def detail(repsvm_tipo_sentencia_id):
    """Detalle de un Tipo de Sentencia"""
    repsvm_tipo_sentencia = REPSVMTipoSentencia.query.get_or_404(repsvm_tipo_sentencia_id)
    return render_template("repsvm_tipos_sentencias/detail.jinja2", repsvm_tipo_sentencia=repsvm_tipo_sentencia)
