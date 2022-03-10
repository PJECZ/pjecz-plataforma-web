"""
Materias Tipos de Juzgados, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.materias_tipos_juzgados.models import MateriaTipoJuzgado
from plataforma_web.blueprints.materias_tipos_juzgados.forms import MateriaTipoJuzgadoForm

MODULO = "MATERIAS TIPOS JUZGADOS"

materias_tipos_juzgados = Blueprint("materias_tipos_juzgados", __name__, template_folder="templates")


@materias_tipos_juzgados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias_tipos_juzgados.route("/materias_tipos_juzgados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tipos de Juzgados"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = MateriaTipoJuzgado.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(MateriaTipoJuzgado.descripcion).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "materia": {
                    "nombre": resultado.materia.nombre,
                    "url": url_for("materias.detail", materia_id=resultado.materia_id),
                },
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=resultado.id),
                },
                "clave": resultado.clave,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@materias_tipos_juzgados.route("/materias_tipos_juzgados")
def list_active():
    """Listado de Tipos de Juzgados activos"""
    return render_template(
        "materias_tipos_juzgados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos de Juzgados",
        estatus="A",
    )


@materias_tipos_juzgados.route("/materias_tipos_juzgados/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Juzgados inactivos"""
    return render_template(
        "materias_tipos_juzgados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tipos de Juzgados inactivos",
        estatus="B",
    )


@materias_tipos_juzgados.route("/materias_tipos_juzgados/<int:materia_tipo_juzgado_id>")
def detail(materia_tipo_juzgado_id):
    """Detalle de un Tipo de Juzgado"""
    materia_tipo_juzgado = MateriaTipoJuzgado.query.get_or_404(materia_tipo_juzgado_id)
    return render_template("materias_tipos_juzgados/detail.jinja2", materia_tipo_juzgado=materia_tipo_juzgado)


@materias_tipos_juzgados.route("/materias_tipos_juzgados/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Tipo de Juzgado"""
    form = MateriaTipoJuzgadoForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if MateriaTipoJuzgado.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
        else:
            materia_tipo_juzgado = MateriaTipoJuzgado(
                materia=form.materia.data,
                clave=safe_clave(form.clave.data),
                descripcion=safe_string(form.descripcion.data),
            )
            materia_tipo_juzgado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Tipo de Juzgado {materia_tipo_juzgado.clave}"),
                url=url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("materias_tipos_juzgados/new.jinja2", form=form)


@materias_tipos_juzgados.route("/materias_tipos_juzgados/edicion/<int:materia_tipo_juzgado_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(materia_tipo_juzgado_id):
    """Editar Tipo de Juzgado"""
    materia_tipo_juzgado = MateriaTipoJuzgado.query.get_or_404(materia_tipo_juzgado_id)
    form = MateriaTipoJuzgadoForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if materia_tipo_juzgado.clave != clave:
            clave_existente = MateriaTipoJuzgado.query.filter_by(clave=clave).first()
            if clave_existente and clave_existente.id != materia_tipo_juzgado_id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            materia_tipo_juzgado.materia = form.materia.data
            materia_tipo_juzgado.clave = safe_clave(form.clave.data)
            materia_tipo_juzgado.descripcion = safe_string(form.descripcion.data)
            materia_tipo_juzgado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Tipo de Juzgado {materia_tipo_juzgado.clave}"),
                url=url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = materia_tipo_juzgado.clave
    return render_template("materias_tipos_juzgados/edit.jinja2", form=form, materia_tipo_juzgado=materia_tipo_juzgado)


@materias_tipos_juzgados.route("/materias_tipos_juzgados/eliminar/<int:materia_tipo_juzgado_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(materia_tipo_juzgado_id):
    """Eliminar Tipo de Juzgado"""
    materia_tipo_juzgado = MateriaTipoJuzgado.query.get_or_404(materia_tipo_juzgado_id)
    if materia_tipo_juzgado.estatus == "A":
        materia_tipo_juzgado.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Tipo de Juzgado {materia_tipo_juzgado.clave}"),
            url=url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id))


@materias_tipos_juzgados.route("/materias_tipos_juzgados/recuperar/<int:materia_tipo_juzgado_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(materia_tipo_juzgado_id):
    """Recuperar Tipo de Juzgado"""
    materia_tipo_juzgado = MateriaTipoJuzgado.query.get_or_404(materia_tipo_juzgado_id)
    if materia_tipo_juzgado.estatus == "B":
        materia_tipo_juzgado.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Tipo de Juzgado {materia_tipo_juzgado.clave}"),
            url=url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=materia_tipo_juzgado.id))
