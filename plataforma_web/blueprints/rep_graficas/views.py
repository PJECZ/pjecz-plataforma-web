"""
Rep Graficas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_graficas.models import RepGrafica

rep_graficas = Blueprint('rep_graficas', __name__, template_folder='templates')


@rep_graficas.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """ Permiso por defecto """


@rep_graficas.route('/rep_graficas')
def list_active():
    """ Listado de Rep Graficas activos """
    rep_graficas_activos = RepGrafica.query.filter(RepGrafica.estatus == 'A').order_by(RepGrafica.creado.desc()).limit(100).all()
    return render_template('rep_graficas/list.jinja2', rep_graficas=rep_graficas_activos, estatus='A')
