"""
Materias Tipos de Juicios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_parameters, output
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio
from plataforma_web.blueprints.materias_tipos_juicios.forms import MateriaTipoJuicioForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

materias_tipos_juicios = Blueprint("materias_tipos_juicios", __name__, template_folder="templates")

MODULO = "MATERIAS TIPOS JUICIOS"


@materias_tipos_juicios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias_tipos_juicios.route('/materias_tipos_juicios')
def list_active():
    """Listado de Tipos de Juicios activos"""
    return render_template(
        'materias_tipos_juicios/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Tipos de Juicios',
        estatus='A',
    )



@materias_tipos_juicios.route("/materias/tipos_juicios/<int:materia_tipo_juicio_id>")
def detail(materia_tipo_juicio_id):
    """Detalle de un Materia Tipo de Juicio"""
    materia_tipo_juicio = MateriaTipoJuicio.query.get_or_404(materia_tipo_juicio_id)
    return render_template(
        "materias_tipos_juicios/detail.jinja2",
        materia_tipo_juicio=materia_tipo_juicio,
    )


@materias_tipos_juicios.route("/materias/tipos_juicios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Materia Tipo de Juicio"""
    form = MateriaTipoJuicioForm()
    if form.validate_on_submit():
        materia_tipo_juicio = MateriaTipoJuicio(
            materia=form.materia.data,
            descripcion=safe_string(form.descripcion.data),
        )
        materia_tipo_juicio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Tipo de Juicio {materia_tipo_juicio.descripcion} en {materia_tipo_juicio.materia.nombre}"),
            url=url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("materias_tipos_juicios/new.jinja2", form=form)


@materias_tipos_juicios.route("/materias/tipos_juicios/edicion/<int:materia_tipo_juicio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(materia_tipo_juicio_id):
    """Editar Materia Tipo de Juicio"""
    materia_tipo_juicio = MateriaTipoJuicio.query.get_or_404(materia_tipo_juicio_id)
    form = MateriaTipoJuicioForm()
    if form.validate_on_submit():
        materia_tipo_juicio.materia = form.materia.data
        materia_tipo_juicio.descripcion = safe_string(form.descripcion.data)
        materia_tipo_juicio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado el tipo de juicio {materia_tipo_juicio.descripcion} en {materia_tipo_juicio.materia.nombre}"),
            url=url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.materia.data = materia_tipo_juicio.materia
    form.descripcion.data = materia_tipo_juicio.descripcion
    return render_template("materias_tipos_juicios/edit.jinja2", form=form, materia_tipo_juicio=materia_tipo_juicio)


@materias_tipos_juicios.route("/materias/tipos_juicios/eliminar/<int:materia_tipo_juicio_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(materia_tipo_juicio_id):
    """Eliminar Materia Tipo de Juicio"""
    materia_tipo_juicio = MateriaTipoJuicio.query.get_or_404(materia_tipo_juicio_id)
    if materia_tipo_juicio.estatus == "A":
        materia_tipo_juicio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el tipo de juicio {materia_tipo_juicio.descripcion} de {materia_tipo_juicio.materia.nombre}"),
            url=url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id))


@materias_tipos_juicios.route("/materias/tipos_juicios/recuperar/<int:materia_tipo_juicio_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(materia_tipo_juicio_id):
    """Recuperar Materia Tipo de Juicio"""
    materia_tipo_juicio = MateriaTipoJuicio.query.get_or_404(materia_tipo_juicio_id)
    if materia_tipo_juicio.estatus == "B":
        materia_tipo_juicio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el tipo de juicio {materia_tipo_juicio.descripcion} de {materia_tipo_juicio.materia.nombre}"),
            url=url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=materia_tipo_juicio.id))
