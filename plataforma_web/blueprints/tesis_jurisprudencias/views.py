"""
Tesis y Jurisprudencias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.abogados.models import Abogado
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia

MODULO = "TESIS Y JURISPRUDENCIAS"

tesis_jurisprudencias = Blueprint('tesis_jurisprudencias', __name__, template_folder='templates')


@tesis_jurisprudencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """ Permiso por defecto """


@tesis_jurisprudencias.route('/tesis_jurisprudencias')
def list_active():
    """Listado de Tesis y Jurisprudencias activas"""
    return render_template(
        'tesis_jurisprudencias/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Tesis y Jurisprudencias',
        estatus='A',
    )


@tesis_jurisprudencias.route('/tesis_jurisprudencias/inactivos')
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tesis y Jurisprudencias inactivas"""
    return render_template(
        'tesis_jurisprudencias/list.jinja2',
        filtros=json.dumps({'estatus': 'B'}),
        titulo='Tesis y Jurisprudencias inactivos',
        estatus='B',
    )
