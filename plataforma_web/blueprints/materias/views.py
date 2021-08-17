"""
Materias, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias.forms import MateriaForm
from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio

materias = Blueprint("materias", __name__, template_folder="templates")

MODULO = "MATERIAS"


@materias.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """Permiso por defecto"""


@materias.route("/materias")
def list_active():
    """Listado de Materias activas"""
    return render_template(
        "materias/list.jinja2",
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all(),
        estatus="A",
    )


@materias.route("/materias/inactivos")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def list_inactive():
    """Listado de Materias inactivas"""
    return render_template(
        "materias/list.jinja2",
        materias=Materia.query.filter_by(estatus="B").order_by(Materia.nombre).all(),
        estatus="B",
    )


@materias.route("/materias/<int:materia_id>")
def detail(materia_id):
    """Detalle de una Materia"""
    materia = Materia.query.get_or_404(materia_id)
    return render_template(
        "materias/detail.jinja2",
        materia=materia,
        autoridades=Autoridad.query.filter(Autoridad.materia == materia).filter_by(estatus="A").all(),
        materias_tipos_juicios=MateriaTipoJuicio.query.filter(MateriaTipoJuicio.materia == materia).filter_by(estatus="A").all(),
    )


@materias.route("/materias/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CATALOGOS)
def new():
    """Nueva Materia"""
    form = MateriaForm()
    if form.validate_on_submit():
        materia = Materia(nombre=safe_string(form.nombre.data))
        materia.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nueva materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("materias/new.jinja2", form=form)


@materias.route("/materias/edicion/<int:materia_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def edit(materia_id):
    """Editar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    form = MateriaForm()
    if form.validate_on_submit():
        materia.nombre = safe_string(form.nombre.data)
        materia.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Editada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = materia.nombre
    return render_template("materias/edit.jinja2", form=form, materia=materia)


@materias.route("/materias/eliminar/<int:materia_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(materia_id):
    """Eliminar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "A":
        materia.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Eliminada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))


@materias.route("/materias/recuperar/<int:materia_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(materia_id):
    """Recuperar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "B":
        materia.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Recuperada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))
