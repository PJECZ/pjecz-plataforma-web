"""
Peritos, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.peritos.models import Perito

peritos = Blueprint('peritos', __name__, template_folder='templates')


@peritos.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    pass


@peritos.route('/peritos')
def list_active():
    """ Listado de Peritos """
    peritos_activos = Perito.query.filter(Perito.estatus == 'A').all()
    return render_template('peritos/list.jinja2', peritos=peritos_activos)


@peritos.route('/peritos/<int:perito_id>')
def detail(perito_id):
    """ Detalle de un Perito """
    perito = Perito.query.get_or_404(perito_id)
    return render_template('peritos/detail.jinja2', perito=perito)
