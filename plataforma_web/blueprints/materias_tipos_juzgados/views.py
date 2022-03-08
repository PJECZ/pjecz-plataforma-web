"""
Materias Tipos de Juzgados, vistas
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
from plataforma_web.blueprints.materias_tipos_juzgados.models import MateriaTipoJuzgado

MODULO = "MATERIAS TIPOS JUZGADOS"

materias_tipos_juzgados = Blueprint("materias_tipos_juzgados", __name__, template_folder="templates")


@materias_tipos_juzgados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias_tipos_juzgados.route("/materias_tipos_juzgados")
def list_active():
    """Listado de Tipos de Juzgados activos"""
    materias_tipos_juzgados_activos = MateriaTipoJuzgado.query.filter(MateriaTipoJuzgado.estatus == "A").all()
    return render_template(
        "materias_tipos_juzgados/list.jinja2",
        materias_tipos_juzgados=materias_tipos_juzgados_activos,
        titulo="Tipos de Juzgados",
        estatus="A",
    )


@materias_tipos_juzgados.route("/materias_tipos_juzgados/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Juzgados inactivos"""
    materias_tipos_juzgados_inactivos = MateriaTipoJuzgado.query.filter(MateriaTipoJuzgado.estatus == "B").all()
    return render_template(
        "materias_tipos_juzgados/list.jinja2",
        materias_tipos_juzgados=materias_tipos_juzgados_inactivos,
        titulo="Tipos de Juzgados inactivos",
        estatus="B",
    )


@materias_tipos_juzgados.route("/materias_tipos_juzgados/<int:materia_tipo_juzgado_id>")
def detail(materia_tipo_juzgado_id):
    """Detalle de un Tipo de Juzgado"""
    materia_tipo_juzgado = MateriaTipoJuzgado.query.get_or_404(materia_tipo_juzgado_id)
    return render_template("materias_tipos_juzgados/detail.jinja2", materia_tipo_juzgado=materia_tipo_juzgado)
