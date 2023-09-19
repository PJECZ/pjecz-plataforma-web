"""
Estadisticas Informes Registros, vistas
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
from plataforma_web.blueprints.est_informes.models import EstInforme
from plataforma_web.blueprints.est_variables.models import EstVariable
from plataforma_web.blueprints.est_informes_registros.models import EstInformeRegistro

MODULO = "ESTADISTICAS INFORMES REGISTROS"

est_informes_registros = Blueprint("est_informes_registros", __name__, template_folder="templates")


@est_informes_registros.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@est_informes_registros.route("/est_informes_registros/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de registros"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EstInformeRegistro.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "est_informe_id" in request.form:
        est_informe = EstInforme.query.get(request.form["est_informe_id"])
        if est_informe:
            consulta = consulta.filter_by(est_informe=est_informe)
    if "est_variable_id" in request.form:
        est_variable = EstVariable.query.get(request.form["est_variable_id"])
        if est_variable:
            consulta = consulta.filter_by(est_variable=est_variable)
    registros = consulta.order_by(EstInformeRegistro.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("est_informes_registros.detail", est_informe_registro_id=resultado.id),
                },
                "autoridad_clave": resultado.est_informe.autoridad.clave,
                "est_informe": {
                    "fecha": resultado.est_informe.fecha.strftime("%Y-%m-%d"),
                    "url": url_for("est_informes.detail", est_informe_id=resultado.est_informe.id),
                },
                "est_variable_clave": resultado.est_variable.clave,
                "est_variable_descripcion": resultado.est_variable.descripcion,
                "cantidad": resultado.cantidad if resultado.cantidad is not None else "ND",
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@est_informes_registros.route("/est_informes_registros")
def list_active():
    """Listado de registros activos"""
    return render_template(
        "est_informes_registros/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Registros de estadísticas",
        estatus="A",
    )


@est_informes_registros.route("/est_informes_registros/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de registros inactivos"""
    return render_template(
        "est_informes_registros/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Registros inactivos de estadísticas",
        estatus="B",
    )


@est_informes_registros.route("/est_informes_registros/<int:est_informe_registro_id>")
def detail(est_informe_registro_id):
    """Detalle de un registro"""
    est_informe_registro = EstInformeRegistro.query.get_or_404(est_informe_registro_id)
    return render_template("est_informes_registros/detail.jinja2", est_informe_registro=est_informe_registro)
