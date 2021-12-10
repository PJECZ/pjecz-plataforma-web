"""
Tesis Jusridprudencias Funcionarios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.tesis_jurisprudencias_funcionarios.models import TesisJurisprudenciaFuncionario

MODULO = "TESIS JURISPRUDENCIAS"

tesis_jurisprudencias_funcionarios = Blueprint('tesis_jurisprudencias_funcionarios', __name__, template_folder='templates')


@tesis_jurisprudencias_funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """ Permiso por defecto """

@tesis_jurisprudencias_funcionarios.route('/tesis_jurisprudencias_funcionarios')
def list_active():
    """ Listado de Funcionarios que tienen una Tesis y Jurisprudencia activos """
    funcionarios_activos = TesisJurisprudenciasFuncionarios.query.filter(TesisJurisprudenciasFuncionarios.estatus == 'A').all()
    return render_template(
        'tesis_jurisprudencias_funcionarios/list.jinja2', 
        funcionarios=funcionarios_activos, 
        titulo='Funcionarios que tienen una Tesis y Jurisprudencia ', 
        estatus='A',)

