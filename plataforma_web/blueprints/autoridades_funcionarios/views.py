"""
Autoridades Funcionarios, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.autoridades_funcionarios.models import AutoridadFuncionario

MODULO = "AUTORIDADES FUNCIONARIOS"

autoridades_funcionarios = Blueprint("autoridades_funcionarios", __name__, template_folder="templates")


@autoridades_funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades_funcionarios.route("/autoridades_funcionarios")
def list_active():
    """Listado de Autoridades Funcionarios activos"""
    autoridades_funcionarios_activos = AutoridadFuncionario.query.filter(AutoridadFuncionario.estatus == "A").all()
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        autoridades_funcionarios=autoridades_funcionarios_activos,
        titulo="Autoridades Funcionarios",
        estatus="A",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades Funcionarios inactivos"""
    autoridades_funcionarios_inactivos = AutoridadFuncionario.query.filter(AutoridadFuncionario.estatus == "B").all()
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        autoridades_funcionarios=autoridades_funcionarios_inactivos,
        titulo="Autoridades Funcionarios inactivos",
        estatus="B",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/<int:autoridad_funcionario_id>")
def detail(autoridad_funcionario_id):
    """Detalle de un Autoridad Funcuionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    return render_template("autoridades_funcionarios/detail.jinja2", autoridad_funcionario=autoridad_funcionario)
