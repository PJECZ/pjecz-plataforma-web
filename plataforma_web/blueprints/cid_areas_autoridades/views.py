"""
CID Areas-Autoridades, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.cid_areas_autoridades.models import CIDAreaAutoridad

MODULO = "CID AREAS AUTORIDADES"

cid_areas_autoridades = Blueprint("cid_areas_autoridades", __name__, template_folder="templates")


@cid_areas_autoridades.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_areas_autoridades.route("/cid_areas_autoridades/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Areas-Autoridades"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CIDAreaAutoridad.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(CIDAreaAutoridad.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("cid_areas_autoridades.detail", cid_area_autoridad_id=resultado.id),
                },
                "cid_area": {
                    "clave": resultado.cid_area.clave,
                    "url": url_for("cid_areas.detail", cid_area_id=resultado.cid_area_id) if current_user.can_view("CID AREAS") else "",
                },
                "autoridad": {
                    "clave": resultado.autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad_id) if current_user.can_view("AUTORIDADES") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cid_areas_autoridades.route("/cid_areas_autoridades")
def list_active():
    """Listado de Areas-Autoridades activas"""
    return render_template(
        "cid_areas_autoridades/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Areas-Autoridades",
        estatus="A",
    )


@cid_areas_autoridades.route("/cid_areas_autoridades/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Areas-Autoridades inactivas"""
    return render_template(
        "cid_areas_autoridades/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Areas-Autoridades inactivos",
        estatus="B",
    )


@cid_areas_autoridades.route("/cid_areas_autoridades/<int:cid_area_autoridad_id>")
def detail(cid_area_autoridad_id):
    """Detalle de un Area-Autoridad"""
    cid_area_autoridad_id = CIDAreaAutoridad.query.get_or_404(cid_area_autoridad_id)
    return render_template("cid_areas_autoridades/detail.jinja2", cid_area_autoridad_id=cid_area_autoridad_id)
