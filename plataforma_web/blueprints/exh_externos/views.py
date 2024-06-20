"""
Exh Externos, vistas
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
from plataforma_web.blueprints.exh_externos.models import ExhExterno

MODULO = "EXH EXTERNOS"

exh_externos = Blueprint("exh_externos", __name__, template_folder="templates")


@exh_externos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_externos.route("/exh_externos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Exh Externo"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExterno.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(ExhExterno.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("exh_externos.detail", exh_externo_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_externos.route("/exh_externos")
def list_active():
    """Listado de Exh Externo activos"""
    return render_template(
        "exh_externos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Externos",
        estatus="A",
    )


@exh_externos.route("/exh_externos/<int:exh_externo_id>")
def detail(exh_externo_id):
    """Detalle de un Exh Externo"""
    exh_externo = ExhExterno.query.get_or_404(exh_externo_id)
    return render_template("exh_externos/detail.jinja2", exh_externo=exh_externo)
