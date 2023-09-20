"""
Estadisticas Informes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.est_informes.models import EstInforme

MODULO = "ESTADISTICAS INFORMES"

est_informes = Blueprint("est_informes", __name__, template_folder="templates")


@est_informes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@est_informes.route("/est_informes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de informes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EstInforme.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(EstInforme.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(EstInforme.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(EstInforme.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                    "url": url_for("est_informes.detail", est_informe_id=resultado.id),
                },
                "autoridad": resultado.autoridad.clave,
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@est_informes.route("/est_informes")
def list_active():
    """Listado de informes activos"""
    return render_template(
        "est_informes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Informes de estadísticas",
        estatus="A",
    )


@est_informes.route("/est_informes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de informes inactivos"""
    return render_template(
        "est_informes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Informes inactivos de estadísticas",
        estatus="B",
    )


@est_informes.route("/est_informes/<int:est_informe_id>")
def detail(est_informe_id):
    """Detalle de un informe"""
    est_informe = EstInforme.query.get_or_404(est_informe_id)
    return render_template("est_informes/detail.jinja2", est_informe=est_informe)
