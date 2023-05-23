"""
SIGA Grabaciones, vistas
"""
import json
from flask import Blueprint, request, render_template, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.siga_grabaciones.models import SIGAGrabacion
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "SIGA_GRABACIONES"

siga_grabaciones = Blueprint("siga_grabaciones", __name__, template_folder="templates")


@siga_grabaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@siga_grabaciones.route("/siga_grabaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de siga_grabaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SIGAGrabacion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "desde" in request.form:
        consulta = consulta.filter(SIGAGrabacion.modificado >= request.form["desde"])
    if "hasta" in request.form:
        consulta = consulta.filter(SIGAGrabacion.modificado <= request.form["hasta"] + " 23:59:59")
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    registros = consulta.order_by(SIGAGrabacion.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("siga_grabaciones.detail", siga_grabacion_id=resultado.id),
                },
                "tiempo": {
                    "inicio": resultado.inicio.strftime("%Y/%m/%d - %H:%M:%S"),
                    "termino": resultado.termino.strftime("%Y/%m/%d - %H:%M:%S"),
                },
                "sala": {
                    "nombre": resultado.siga_sala.clave,
                    "url": url_for("siga_salas.detail", siga_sala_id=resultado.siga_sala.id),
                },
                "inicio": resultado.inicio.strftime("%Y/%m/%d - %H:%M:%S"),
                "termino": resultado.termino.strftime("%Y/%m/%d - %H:%M:%S"),
                "autoridad_materia": {
                    "autoridad": {
                        "nombre": resultado.autoridad.clave,
                        "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                    },
                    "materia": {
                        "nombre": resultado.materia.nombre,
                        "url": url_for("materias.detail", materia_id=resultado.materia.id),
                    },
                },
                "autoridad": {
                    "nombre": resultado.autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                },
                "materia": {
                    "nombre": resultado.materia.nombre,
                    "url": url_for("materias.detail", materia_id=resultado.materia.id),
                },
                "expediente": resultado.expediente,
                "duracion": resultado.duracion.strftime("%H:%M:%S"),
                "estado": resultado.estado,
                "nota": resultado.nota,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@siga_grabaciones.route("/siga_grabaciones")
def list_active():
    """Listado de Grabaciones activas"""
    return render_template(
        "siga_grabaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="SIGA Grabaciones",
        estatus="A",
    )


@siga_grabaciones.route("/siga_grabaciones/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Grabaciones inactivas"""
    return render_template(
        "siga_grabaciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="SIGA Grabaciones Inactivas",
        estatus="B",
    )


@siga_grabaciones.route("/siga_grabaciones/<int:siga_grabacion_id>")
def detail(siga_grabacion_id):
    """Detalle de un SIGAGrabacion"""
    siga_grabacion = SIGAGrabacion.query.get_or_404(siga_grabacion_id)
    return render_template(
        "siga_grabaciones/detail.jinja2",
        siga_grabacion=siga_grabacion,
        filtros=json.dumps({"estatus": "A"}),
        estados_bitacoras=SIGAGrabacion.ESTADOS,
    )
