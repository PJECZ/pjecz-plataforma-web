"""
Funcionarios, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.funcionarios.models import Funcionario

MODULO = "FUNCIONARIOS"

funcionarios = Blueprint("funcionarios", __name__, template_folder="templates")


@funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@funcionarios.route("/funcionarios")
def list_active():
    """Listado de Funcionarios activos"""
    funcionarios_activos = Funcionario.query.filter(Funcionario.estatus == "A").all()
    return render_template(
        "funcionarios/list.jinja2",
        funcionarios=funcionarios_activos,
        titulo="Funcionarios",
        estatus="A",
    )


@funcionarios.route("/funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Funcionarios inactivos"""
    funcionarios_inactivos = Funcionario.query.filter(Funcionario.estatus == "B").all()
    return render_template(
        "funcionarios/list.jinja2",
        funcionarios=funcionarios_inactivos,
        titulo="Funcionarios inactivos",
        estatus="B",
    )


@funcionarios.route("/funcionarios/<int:funcionario_id>")
def detail(funcionario_id):
    """Detalle de un Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    return render_template("funcionarios/detail.jinja2", funcionario=funcionario)
