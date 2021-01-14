"""
Distritos, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.distritos.models import Distrito

distritos = Blueprint('distritos', __name__, template_folder='templates')


@distritos.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    pass


@distritos.route('/distritos')
def list_active():
    """ Listado de distritos """
    distritos_activos = Distrito.query.filter(Distrito.estatus == 'A').all()
    return render_template('distritos/list.jinja2', distritos=distritos_activos)


@distritos.route('/distritos/<int:distrito_id>')
def detail(distrito_id):
    """ Detalle de un distrito """
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template('distritos/detail.jinja2', distrito=distrito)
