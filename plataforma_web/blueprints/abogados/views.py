"""
Abogados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.abogados.models import Abogado

abogados = Blueprint('abogados', __name__, template_folder='templates')

@abogados.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    pass


@abogados.route('/abogados')
def list_active():
    """ Listado de Abogados """
    abogados_activos = Abogado.query.filter(Abogado.estatus == 'A').all()
    return render_template('abogados/list.jinja2', abogados=abogados_activos)


@abogados.route('/abogados/<int:abogado_id>')
def detail(abogado_id):
    """ Detalle de un Abogado """
    abogado = Abogado.query.get_or_404(abogado_id)
    return render_template('abogados/detail.jinja2', abogado=abogado)
