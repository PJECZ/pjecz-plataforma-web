"""
Modulos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.modulos.models import Modulo

modulos = Blueprint("modulos", __name__, template_folder="templates")


@modulos.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@modulos.route("/modulos")
def list_active():
    """Listado de Módulos activos"""
    modulos_activos = Modulo.query.filter(Modulo.estatus == "A").order_by(Modulo.nombre).all()
    return render_template("modulos/list.jinja2", modulos=modulos_activos, estatus="A")


@modulos.route("/modulos/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Módulos inactivos"""
    modulos_inactivos = Modulo.query.filter(Modulo.estatus == "B").order_by(Modulo.nombre).all()
    return render_template("modulos/list.jinja2", modulos=modulos_inactivos, estatus="B")


@modulos.route('/modulos/<int:modulo_id>')
def detail(modulo_id):
    """ Detalle de un Módulo """
    modulo = Modulo.query.get_or_404(modulo_id)
    return render_template('modulos/detail.jinja2', modulo=modulo)


@modulos.route('/modulos/eliminar/<int:modulo_id>')
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(modulo_id):
    """ Eliminar Módulo """
    modulo = Modulo.query.get_or_404(modulo_id)
    if modulo.estatus == 'A':
        modulo.delete()
        flash(f'Módulo {modulo.nombre} eliminado.', 'success')
    return redirect(url_for('modulos.detail', modulo_id=modulo.id))


@modulos.route('/modulos/recuperar/<int:modulo_id>')
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(modulo_id):
    """ Recuperar Módulo """
    modulo = Modulo.query.get_or_404(modulo_id)
    if modulo.estatus == 'B':
        modulo.recover()
        flash(f'Módulo {modulo.nombre} recuperado.', 'success')
    return redirect(url_for('modulos.detail', modulo_id=modulo.id))
