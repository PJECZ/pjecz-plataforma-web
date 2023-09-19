"""
Estadisticas Variables, vistas
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
from plataforma_web.blueprints.est_variables.models import EstVariable

MODULO = "ESTADISTICAS VARIABLES"

est_variables = Blueprint("est_variables", __name__, template_folder="templates")


@est_variables.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@est_variables.route("/est_variables/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Variables"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EstVariable.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(EstVariable.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("est_variables.detail", est_variable_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@est_variables.route("/est_variables")
def list_active():
    """Listado de Variables activas"""
    return render_template(
        "est_variables/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Variables de estadísticas",
        estatus="A",
    )


@est_variables.route("/est_variables/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Variables inactivas"""
    return render_template(
        "est_variables/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Variables inactivas de estadísticas",
        estatus="B",
    )


@est_variables.route("/est_variables/<int:est_variable_id>")
def detail(est_variable_id):
    """Detalle de una Variable"""
    est_variable = EstVariable.query.get_or_404(est_variable_id)
    return render_template("est_variables/detail.jinja2", est_variable=est_variable)
