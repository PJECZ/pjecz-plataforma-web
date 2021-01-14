"""
Autoridades, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad

autoridades = Blueprint('autoridades', __name__, template_folder='templates')


@autoridades.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    pass


@autoridades.route('/autoridades')
def list_active():
    """ Listado de autoridades """
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == 'A').all()
    return render_template('autoridades/list.jinja2', autoridades=autoridades_activas)


@autoridades.route('/autoridades/<int:autoridad_id>')
def detail(autoridad_id):
    """ Detalle de una autoridad """
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    return render_template('autoridades/detail.jinja2', autoridad=autoridad)
