"""
CITAS Clientes, vistas
"""
import json

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib import datatables

from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_expedientes.models import CITExpediente

from plataforma_web.blueprints.cit_expedientes.forms import CITExpedienteSearchForm

MODULO = "CIT EXPEDIENTES"

cit_expedientes = Blueprint("cit_expedientes", __name__, template_folder="templates")


@cit_expedientes.route("/cit_expedientes")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Cliente activos"""
    activos = CITExpediente.query.filter(CITExpediente.estatus == "A").all()
    return render_template(
        "cit_expedientes/list.jinja2",
        expedientes=activos,
        titulo="Expedientes",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_expedientes.route("/cit_expedientes/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Cliente inactivos"""
    inactivos = CITExpediente.query.filter(CITExpediente.estatus == "B").all()
    return render_template(
        "cit_expedientes/list.jinja2",
        expedientes=inactivos,
        titulo="Expedientes inactivos",
        estatus="B",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_expedientes.route("/cit_expedientes/<int:expediente_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(expediente_id):
    """Detalle de un Expediente"""
    expediente = CITExpediente.query.get_or_404(expediente_id)
    return render_template("cit_expedientes/detail.jinja2", expediente=expediente)

@cit_expedientes.route("/cit_expedientes/buscar", methods=["GET", "POST"])
def search():
    """Buscar un Expediente"""
    form_search = CITExpedienteSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []

        # Nombres
        if form_search.expediente.data:
            busqueda["expediente"] = form_search.expediente.data
            titulos.append("expediente " + busqueda["expediente"])

        # Mostrar resultados
        return render_template(
            "cit_expedientes/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Expedientes con " + ", ".join(titulos),
        )

    return render_template("cit_expedientes/search.jinja2", form=form_search)


@cit_expedientes.route("/cit_expedientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de expedientes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()

    # Consultar
    consulta = CITExpediente.query

    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")

    if "expediente" in request.form:
        consulta = consulta.filter(CITExpediente.expediente.like("%" + safe_string(request.form["expediente"]) + "%"))

    registros = consulta.order_by(CITExpediente.expediente.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for expediente in registros:
        data.append(
            {
                "expediente": {
                    "id": expediente.id,
                    "url": url_for("cit_expedientes.detail", expediente_id=expediente.id),
                    "descripcion": expediente.expediente,
                },
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)
