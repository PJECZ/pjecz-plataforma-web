"""
Listas de Acuerdos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

listas_de_acuerdos = Blueprint('listas_de_acuerdos', __name__, template_folder='templates')


@listas_de_acuerdos.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    pass


@listas_de_acuerdos.route('/listas_de_acuerdos')
def list_active():
    """ Listado de Listas de Acuerdos """
    listas_de_acuerdos_activos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == 'A').all()
    return render_template('listas_de_acuerdos/list.jinja2', listas_de_acuerdos=listas_de_acuerdos_activos)


@listas_de_acuerdos.route('/listas_de_acuerdos/<int:lista_de_acuerdo_id>')
def detail(lista_de_acuerdo_id):
    """ Detalle de un Lista de Acuerdo """
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    return render_template('listas_de_acuerdos/detail.jinja2', lista_de_acuerdo=lista_de_acuerdo)
