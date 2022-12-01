"""
REPSVM Agresores-Delitos, vistas
"""
import json
from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.repsvm_agresores_delitos.models import REPSVMAgresorDelito

MODULO = "REPSVM AGRESORES DELITOS"

repsvm_agresores_delitos = Blueprint("repsvm_agresores_delitos", __name__, template_folder="templates")


@repsvm_agresores_delitos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_agresores_delitos.route("/repsvm_agresores_delitos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Agresores-Delitos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = REPSVMAgresorDelito.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(REPSVMAgresorDelito.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("repsvm_agresores_delitos.detail", repsvm_agresor_delito_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@repsvm_agresores_delitos.route("/repsvm_agresores_delitos")
def list_active():
    """Listado de Agresores-Delitos activos"""
    return render_template(
        "repsvm_agresores_delitos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Agresores-Delitos",
        estatus="A",
    )


@repsvm_agresores_delitos.route("/repsvm_agresores_delitos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Agresores-Delitos inactivos"""
    return render_template(
        "repsvm_agresores_delitos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Agresores-Delitos inactivos",
        estatus="B",
    )


@repsvm_agresores_delitos.route("/repsvm_agresores_delitos/<int:repsvm_agresor_delito_id>")
def detail(repsvm_agresor_delito_id):
    """Detalle de un Agresor-Delito"""
    repsvm_agresor_delito = REPSVMAgresorDelito.query.get_or_404(repsvm_agresor_delito_id)
    return render_template("repsvm_agresores_delitos/detail.jinja2", repsvm_agresor_delito=repsvm_agresor_delito)
