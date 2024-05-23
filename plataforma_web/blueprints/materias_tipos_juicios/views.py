"""
Materias Tipos de Juicios, vistas
"""

import datetime
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.materias.models import Materia
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


@materias_tipos_juicios.route("/materias_tipos_juicios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tipos de Juicios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = MateriaTipoJuicio.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "materia_id" in request.form:
        consulta = consulta.filter_by(materia_id=request.form["materia_id"])
    if "descripcion" in request.form:
        consulta = consulta.filter_by(descripcion=request.form["descripcion"])
    registros = consulta.order_by(MateriaTipoJuicio.descripcion).offset(start).limit(rows_per_page).all()
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
                    "url": url_for("materias_tipos_juicios.detail", materia_tipo_juicio_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@materias_tipos_juicios.route("/materias_tipos_juicios/select_json/<int:materia_id>", methods=["GET", "POST"])
def select_json(materia_id=None):
    """Select JSON para materias tipos juicios"""
    # Si materia_id es None, entonces no se entregan tipos juicios
    if materia_id is None:
        return json.dumps([])
    # Consultar
    consulta = MateriaTipoJuicio.query.filter_by(materia_id=materia_id, estatus="A")
    # Ordenar
    consulta = consulta.order_by(MateriaTipoJuicio.descripcion)
    # Elaborar datos para Select
    data = []
    for resultado in consulta.all():
        data.append(
            {
                "id": resultado.id,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return json.dumps(data)


@materias_tipos_juicios.route("/materias_tipos_juicios")
def list_active():
    """Listado de Tipos de Juicios activos"""
    return render_template(
        "materias_tipos_juicios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos de Juicios",
        estatus="A",
    )


@materias_tipos_juicios.route("/materias_tipos_juicios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Juicios inactivos"""
    return render_template(
        "materias_tipos_juicios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tipos de Juicios inactivos",
        estatus="B",
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


@materias_tipos_juicios.route("/materias/tipos_juicios/reporte", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def report_autoridad(autoridad_id):
    """Reporte de Tipos de Juicios por Autoridad"""

    # La fecha de hoy
    hoy = datetime.date.today()

    # La fecha del primer día del mes actual
    fecha_dia_uno_mes_actual = datetime.date(hoy.year, hoy.month, 1)

    # Tomar valores que vienen en la URL
    autoridad_id = request.args.get("autoridad_id", None)
    fecha_desde = request.args.get("fecha_desde", fecha_dia_uno_mes_actual)
    fecha_hasta = request.args.get("fecha_hasta", hoy)

    # Si no viene la autoridad, mostrar error y redireccionar al listado de tipos de juicios
    if not autoridad_id:
        flash("Error: falta el ID de la autoridad.", "warning")
        return redirect(url_for("materias_tipos_juicios.list_active"))

    # Consultar la autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)

    # Entregar pagina
    return render_template(
        "materias_tipos_juicios/report.jinja2",
        autoridad=autoridad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        filtros=json.dumps(
            {
                "autoridad_id": autoridad.id,
                "estatus": "A",
                "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
            }
        ),
    )
