"""
Materias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias.forms import MateriaForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

materias = Blueprint("materias", __name__, template_folder="templates")

MODULO = "MATERIAS"


@materias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias.route("/materias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Materias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Materia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(Materia.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("materias.detail", materia_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@materias.route("/materias")
def list_active():
    """Listado de Materias activos"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Materias",
        estatus="A",
    )


@materias.route("/materias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Materias inactivos"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Materias inactivos",
        estatus="B",
    )


@materias.route("/materias/<int:materia_id>")
def detail(materia_id):
    """Detalle de una Materia"""
    materia = Materia.query.get_or_404(materia_id)
    return render_template("materias/detail.jinja2", materia=materia)


@materias.route("/materias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Materia"""
    form = MateriaForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if Materia.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
        else:
            materia = Materia(nombre=nombre)
            materia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva materia {materia.nombre}"),
                url=url_for("materias.detail", materia_id=materia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("materias/new.jinja2", form=form)


@materias.route("/materias/edicion/<int:materia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(materia_id):
    """Editar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    form = MateriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if materia.nombre != nombre:
            materia_existente = Materia.query.filter_by(nombre=nombre).first()
            if materia_existente and materia_existente.id != materia_id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            materia.nombre = nombre
            materia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
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
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(materia_id):
    """Eliminar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "A":
        materia.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))


@materias.route("/materias/recuperar/<int:materia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(materia_id):
    """Recuperar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "B":
        materia.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))
