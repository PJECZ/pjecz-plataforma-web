"""
SIGA Bitacoras, vistas
"""
from flask import Blueprint, request
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.siga_bitacoras.models import SIGABitacora
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "SIGA_SALAS"  # Utilizo el nombre del módulo de SALAS para evitar dar de alta otro módulo y sus permisos

siga_bitacoras = Blueprint("siga_bitacoras", __name__, template_folder="templates")


@siga_bitacoras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@siga_bitacoras.route("/siga_bitacoras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de siga_bitacoras"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SIGABitacora.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "desde" in request.form:
        consulta = consulta.filter(SIGABitacora.modificado >= request.form["desde"])
    if "hasta" in request.form:
        consulta = consulta.filter(SIGABitacora.modificado <= request.form["hasta"] + " 23:59:59")
    if "accion" in request.form:
        consulta = consulta.filter_by(accion=request.form["accion"])
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    registros = consulta.order_by(SIGABitacora.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "tiempo": resultado.modificado.strftime("%Y/%m/%d - %H:%M:%S"),
                "accion": resultado.accion,
                "estado": resultado.estado,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)
