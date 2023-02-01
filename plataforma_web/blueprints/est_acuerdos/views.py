"""
Estadisticas Acuerdos, vistas
"""
import json
from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.est_acuerdos.models import EstAcuerdo

MODULO = "EST ACUERDOS"

est_acuerdos = Blueprint("est_acuerdos", __name__, template_folder="templates")


@est_acuerdos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@est_acuerdos.route("/est_acuerdos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de acuerdos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EstAcuerdo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(EstAcuerdo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("est_acuerdos.detail", est_acuerdo_id=resultado.id),
                },
                "distrito_nombre": resultado.distrito_nombre,
                "autoridad_descripcion": resultado.autoridad_descripcion,
                "folio": resultado.folio,
                "expediente": resultado.expediente,
                "numero_caso": resultado.numero_caso,
                "fecha_elaboracion": resultado.fecha_elaboracion,
                "fecha_validacion": resultado.fecha_validacion,
                "fecha_autorizacion": resultado.fecha_autorizacion,
                "estado": resultado.estado,
                "secretario": resultado.secretario,
                "juez": resultado.juez,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@est_acuerdos.route("/est_acuerdos")
def list_active():
    """Listado de Acuerdos activos"""
    return render_template(
        "est_acuerdos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Acuerdos",
        estatus="A",
    )


@est_acuerdos.route("/est_acuerdos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Acuerdos inactivos"""
    return render_template(
        "est_acuerdos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Acuerdos inactivos",
        estatus="B",
    )


@est_acuerdos.route("/est_acuerdos/<int:est_acuerdo_id>")
def detail(est_acuerdo_id):
    """Detalle de un Acuerdo"""
    est_acuerdo = EstAcuerdo.query.get_or_404(est_acuerdo_id)
    return render_template("est_acuerdos/detail.jinja2", est_acuerdo=est_acuerdo)
