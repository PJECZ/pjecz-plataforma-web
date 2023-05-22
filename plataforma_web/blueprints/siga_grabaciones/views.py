"""
SIGA Grabaciones, vistas
"""
import json
from flask import Blueprint, request, render_template
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
        consulta = consulta.filter(SIGAGrabacion.modificado >= request.form['desde'])
    if "hasta" in request.form:
        consulta = consulta.filter(SIGAGrabacion.modificado <= request.form['hasta'] + " 23:59:59")
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form['estado'])
    registros = consulta.order_by(SIGAGrabacion.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "tiempo": resultado.modificado.strftime('%Y/%m/%d - %H:%M:%S'),
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
