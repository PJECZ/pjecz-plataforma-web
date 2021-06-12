"""
Tareas, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.tareas.models import Tarea

tareas = Blueprint("tareas", __name__, template_folder="templates")


@tareas.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """ Permiso por defecto """


@tareas.route("/tareas")
def list_active():
    """ Listado de Tareas """
    tareas_activas = Tarea.query.filter(Tarea.estatus == "A").order_by(Tarea.creado.desc()).limit(100).all()
    return render_template("tareas/list.jinja2", tareas=tareas_activas)
