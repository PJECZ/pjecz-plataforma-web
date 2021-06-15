"""
Materias, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.materias.models import Materia

materias = Blueprint("materias", __name__, template_folder="templates")


@materias.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """Permiso por defecto"""


@materias.route("/materias")
def list_active():
    """Listado de Materias activas"""
    materias_activas = Materia.query.filter(Materia.estatus == "A").order_by(Materia.creado.desc()).all()
    return render_template("materias/list.jinja2", materias=materias_activas, estatus="A")


@materias.route("/materias/inactivos")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def list_inactive():
    """Listado de Materias inactivas"""
    materias_inactivas = Materia.query.filter(Materia.estatus == "B").order_by(Materia.creado.desc()).all()
    return render_template("materias/list.jinja2", materias=materias_inactivas, estatus="B")


@materias.route("/materias/<int:materia_id>")
def detail(materia_id):
    """Detalle de una Materia"""
    materia = Materia.query.get_or_404(materia_id)
    autoridades = Autoridad.query.filter(Autoridad.materia == materia).filter(Autoridad.estatus == "A").all()
    return render_template("materias/detail.jinja2", materia=materia, autoridades=autoridades)


@materias.route("/materias/eliminar/<int:materia_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(materia_id):
    """Eliminar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "A":
        materia.delete()
        flash(f"Materia {materia.nombre} eliminado.", "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))


@materias.route("/materias/recuperar/<int:materia_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(materia_id):
    """Recuperar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "B":
        materia.recover()
        flash(f"Materia {materia.nombre} recuperado.", "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))
