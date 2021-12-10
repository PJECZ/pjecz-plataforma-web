"""
Tesis uriesprudencias Sentencias, vistas
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
from plataforma_web.blueprints.tesis_jurisprudencias_sentencias.models import TesisJurisprudenciaSentencia

MODULO = "TESIS JURISPRUDENCIAS"

tesis_jurisprudencias_sentencias = Blueprint("tesis_jurisprudencias_sentencias", __name__, template_folder="templates")


@tesis_jurisprudencias_sentencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias")
def list_active():
    """Listado de Sentencias de una Tesis o Jurisprudencia"""
    sentencias_activos = TesisJurisprudenciaSentencia.query.filter(TesisJurisprudenciaSentencia.estatus == "A").all()
    return render_template(
        "tesis_jurisprudencias_sentencias/list.jinja2",
        sentencias=sentencias_activos,
        titulo="Sentencias de una Tesis o Jurisprudencia",
        estatus="A",
    )
