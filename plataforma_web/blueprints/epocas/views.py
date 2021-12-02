"""
Epocas, vistas
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
from plataforma_web.blueprints.epocas.models import Epoca

MODULO = "EPOCAS"

epocas = Blueprint('epocas', __name__, template_folder='templates')


@epocas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """ Permiso por defecto """


@epocas.route('/epocas')
def list_active():
    """ Listado de Épocas activas """
    epocas_activas = Epoca.query.filter(Epoca.estatus == 'A').all()
    return render_template('epocas/list.jinja2', epocas=epocas_activas, titulo='Épocas', estatus='A',)


@epocas.route('/epocas/inactivos')
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """ Listado de Épocas inactivas """
    epocas_inactivas = Epoca.query.filter(Epoca.estatus == 'B').all()
    return render_template('epocas/list.jinja2', epocas=epocas_inactivas, titulo='Épocas inactivas', estatus='B',)


@epocas.route('/epocas/<int:epoca_id>')
def detail(epoca_id):
    """ Detalle de un Época """
    epoca = Epoca.query.get_or_404(epoca_id)
    return render_template('epocas/detail.jinja2', epoca=epoca)
