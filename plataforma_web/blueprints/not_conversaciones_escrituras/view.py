"""
Escritura conversación, vistas
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
from plataforma_web.blueprints.not_conversaciones_escrituras.models import NotConversacionEscritura

MODULO = "NOT CONVERSACIONES ESCRITURAS"

not_conversaciones_escrituras = Blueprint("not_conversaciones_escrituras", __name__, template_folder="templates")


@not_conversaciones_escrituras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_conversaciones_escrituras.route("/not_conversaciones_escrituras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Conversaciones Escrituras"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = NotConversacionEscritura.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(NotConversacionEscritura.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("not_conversaciones_escrituras.detail", not_conversacion_escritura_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_conversaciones_escrituras.route("/not_conversaciones_escrituras")
def list_active():
    """Listado de Conversacion Escrituras activos"""
    return render_template(
        "not_conversaciones_escrituras/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Conversacion Escrituras",
        estatus="A",
    )
