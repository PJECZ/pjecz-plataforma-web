"""
CITAS, vistas
"""

from datetime import datetime
import json

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib import datatables

from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_citas.models import CITCita
from plataforma_web.blueprints.cit_expedientes.models import CITExpediente

# from plataforma_web.blueprints.cit_clientes.forms import CITClienteSearchForm

MODULO = "CIT CITAS"

cit_citas = Blueprint("cit_citas", __name__, template_folder="templates")


@cit_citas.route("/cit_citas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Citas activas"""
    activos = CITCita.query.filter(CITCita.estatus == "A").all()
    return render_template(
        "cit_citas/list.jinja2",
        citas=activos,
        titulo="Citas",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_citas.route("/cit_citas/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Cliente inactivos"""
    inactivos = CITCita.query.filter(CITCita.estatus == "B").all()
    return render_template(
        "cit_clientes/list.jinja2",
        clientes=inactivos,
        titulo="Citas inactivas",
        estatus="B",
        filtros=json.dumps({"estatus": "B"}),
    )


@cit_citas.route("/cit_citas/<int:cita_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(cita_id):
    """Detalle de una Cita"""
    cita = CITCita.query.get_or_404(cita_id)
    expedientes = CITExpediente.query.filter(CITExpediente.cita == cita).all()
    return render_template("cit_citas/detail.jinja2", cita=cita, expedientes=expedientes)


@cit_citas.route("/cit_citas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de citas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = CITCita.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")

    registros = consulta.order_by(CITCita.inicio_tiempo.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for cita in registros:
        data.append(
            {
                "id": {
                    "id": cita.id,
                    "url": url_for("cit_citas.detail", cita_id=cita.id),
                },
                "horario": cita.inicio_tiempo.strftime("%Y-%m-%d %H:%M") + " - " + cita.termino_tiempo.strftime("%Y-%m-%d %H:%M"),
                "estado": cita.estado,
                "servicio": cita.servicio.nombre,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)
