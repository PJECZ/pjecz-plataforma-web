"""
Resultados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.resultados.models import Resultado

resultados = Blueprint('resultados', __name__, template_folder='templates')


@resultados.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """ Permiso por defecto """


@resultados.route('/resultados')
def list_active():
    """ Listado de Resultados activos """
    resultados_activos = Resultado.query.filter(Resultado.estatus == 'A').order_by(Resultado.creado.desc()).limit(100).all()
    return render_template('resultados/list.jinja2', resultados=resultados_activos, estatus='A')


@resultados.route('/resultados/inactivos')
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """ Listado de Resultados inactivos """
    resultados_inactivos = Resultado.query.filter(Resultado.estatus == 'B').order_by(Resultado.creado.desc()).limit(100).all()
    return render_template('resultados/list.jinja2', resultados=resultados_inactivos, estatus='B')


@resultados.route('/resultados/<int:resultado_id>')
def detail(resultado_id):
    """ Detalle de un Resultado """
    resultado = Resultado.query.get_or_404(resultado_id)
    return render_template('resultados/detail.jinja2', resultado=resultado)


@resultados.route('/resultados/eliminar/<int:resultado_id>')
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(resultado_id):
    """ Eliminar Resultado """
    resultado = Resultado.query.get_or_404(resultado_id)
    if resultado.estatus == 'A':
        resultado.delete()
        flash(f'Resultado {resultado.descripcion} eliminado.', 'success')
    return redirect(url_for('resultados.detail', resultado_id=resultado.id))
