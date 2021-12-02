"""
Tesis y Jurisprudencias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia

MODULO = "TESIS Y JURISPRUDENCIAS"

tesis_jurisprudencias = Blueprint("tesis_jurisprudencias", __name__, template_folder="templates")


@tesis_jurisprudencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tesis_jurisprudencias.route("/tesis_jurisprudencias")
def list_active():
    """Listado de Tesis Jurisprudencias activos"""
    return render_template(
        "tesis_jurisprudencias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tesis Jurisprudencias",
        estatus="A",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tesis Jurisprudencias inactivos"""
    return render_template(
        "tesis_jurisprudencias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tesis Jurisprudencias inactivos",
        estatus="B",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tesis Jurisprudencias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = TesisJurisprudencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(TesisJurisprudencia.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "titulo": resultado.titulo,
                    "url": url_for("rep_resultados.detail", rep_resultado_id=resultado.id),
                },
                "clase": resultado.clase,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/<int:tesis_jurisprudencia_id>")
def detail(tesis_jurisprudencia_id):
    """Detalle de una Tesis Jurisprudencias"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencia_id)
    return render_template("tesis_jurisprudencias/detail.jinja2", tesis_jurisprudencia=tesis_jurisprudencia)
