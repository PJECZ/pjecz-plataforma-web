"""
Exh Exhortos Partes, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.exh_exhortos_partes.models import ExhExhortoParte

MODULO = "EXH EXHORTOS PARTES"

exh_exhortos_partes = Blueprint("exh_exhortos_partes", __name__, template_folder="templates")


@exh_exhortos_partes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""