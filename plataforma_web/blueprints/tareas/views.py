"""
Tareas, vistas
"""

import json

from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.exceptions import MyAnyError
from lib.google_cloud_storage import get_blob_name_from_url, get_file_from_gcs
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.tareas.models import Tarea

MODULO = "TAREAS"

tareas = Blueprint("tareas", __name__, template_folder="templates")


# @tareas.before_request
# @login_required
# @permission_required(MODULO, Permiso.VER)
# def before_request():
#     """Permiso por defecto"""


@tareas.route("/tareas/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.VER)
def datatable_json():
    """DataTable JSON para listado de Tareas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Tarea.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "comando" in request.form:
        consulta = consulta.filter_by(comando=request.form["comando"])
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    # Ordenar y paginar
    registros = consulta.order_by(Tarea.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "comando": resultado.comando,
                    "url": url_for("tareas.detail", tarea_id=resultado.id),
                },
                "ha_terminado": resultado.ha_terminado,
                "mensaje": resultado.mensaje,
                "usuario": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@tareas.route("/tareas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Tareas activos"""
    return render_template(
        "tareas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tareas",
        estatus="A",
    )


@tareas.route("/tareas/inactivos")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Tareas inactivos"""
    return render_template(
        "tareas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tareas inactivos",
        estatus="B",
    )


@tareas.route("/tareas/<tarea_id>")
@login_required
def detail(tarea_id):
    """Detalle de un Tarea"""
    tarea = Tarea.query.get_or_404(tarea_id)
    return render_template("tareas/detail.jinja2", tarea=tarea)


@tareas.route("/tareas/<tarea_id>/xlsx")
@login_required
def download_xlsx(tarea_id):
    """Descargar archivo XLSX de una Tarea"""

    # Consultar la Tarea
    tarea = Tarea.query.get_or_404(tarea_id)

    # Si no tiene URL, regidir a la página de detalle
    if tarea.url == "":
        flash("Esta tarea no tiene un URL para descargar", "warning")
        return redirect(url_for("tareas.detail", tarea_id=tarea.id))

    # Si no tiene nombre para el archivo, regidir a la página de detalle
    descarga_nombre = tarea.archivo
    if descarga_nombre == "":
        flash("Esta tarea no tiene un archivo para descargar", "warning")
        return redirect(url_for("tareas.detail", tarea_id=tarea.id))

    # Validar que descarga_nombre termine en .xlsx
    if not descarga_nombre.endswith(".xlsx"):
        flash("Esta tarea no tiene un archivo XLSX para descargar", "warning")
        return redirect(url_for("tareas.detail", tarea_id=tarea.id))

    # Obtener el contenido del archivo desde Google Storage
    try:
        descarga_contenido = get_file_from_gcs(
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO"],
            blob_name=get_blob_name_from_url(tarea.url),
        )
    except MyAnyError as error:
        flash(str(error), "danger")
        return redirect(url_for("tareas.detail", tarea_id=tarea.id))

    # Descargar un archivo XLSX
    response = make_response(descarga_contenido)
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response.headers["Content-Disposition"] = f"attachment; filename={descarga_nombre}"
    return response
