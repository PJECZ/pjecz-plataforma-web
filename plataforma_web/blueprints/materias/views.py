"""
Materias, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.materias.models import Materia

materias = Blueprint('materias', __name__, template_folder='templates')


@materias.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """ Permiso por defecto """


@materias.route('/materias')
def list_active():
    """ Listado de Materias activas """
    materias_activas = Materia.query.filter(Materia.estatus == 'A').order_by(Materia.creado.desc()).all()
    return render_template('materias/list.jinja2', materias=materias_activas, estatus='A')


@materias.route('/materias/inactivos')
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def list_inactive():
    """ Listado de Materias inactivas """
    materias_inactivas = Materia.query.filter(Materia.estatus == 'B').order_by(Materia.creado.desc()).all()
    return render_template('materias/list.jinja2', materias=materias_inactivas, estatus='B')


@materias.route('/materias/<int:materia_id>')
def detail(materia_id):
    """ Detalle de una Materia """
    materia = Materia.query.get_or_404(materia_id)
    return render_template('materias/detail.jinja2', materia=materia)
