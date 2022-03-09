"""
Cit Citas Expedientes, vistas
"""
import json

from flask import Blueprint, request, render_template, url_for
from flask_login import login_required
from lib import datatables

from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.cit_citas_expedientes.models import CitCitaExpediente
from plataforma_web.blueprints.cit_citas_expedientes.forms import CitCitaExpedienteSearchForm
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo

MODULO = "CIT EXPEDIENTES"

cit_citas_expedientes = Blueprint("cit_citas_expedientes", __name__, template_folder="templates")


@cit_citas_expedientes.route("/cit_citas_expedientes")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Cliente activos"""
    activos = CitCitaExpediente.query.filter(CitCitaExpediente.estatus == "A").all()
    return render_template(
        "cit_citas_expedientes/list.jinja2",
        expedientes=activos,
        titulo="Expedientes",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_citas_expedientes.route("/cit_citas_expedientes/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Cliente inactivos"""
    inactivos = CitCitaExpediente.query.filter(CitCitaExpediente.estatus == "B").all()
    return render_template(
        "cit_citas_expedientes/list.jinja2",
        expedientes=inactivos,
        titulo="Expedientes inactivos",
        estatus="B",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_citas_expedientes.route("/cit_citas_expedientes/<int:expediente_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(expediente_id):
    """Detalle de un Expediente"""
    expediente = CitCitaExpediente.query.get_or_404(expediente_id)
    return render_template("cit_citas_expedientes/detail.jinja2", expediente=expediente)


@cit_citas_expedientes.route("/cit_citas_expedientes/buscar", methods=["GET", "POST"])
def search():
    """Buscar un Expediente"""
    form_search = CitCitaExpedienteSearchForm()
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
    return render_template("cit_citas_expedientes/search.jinja2", form=form_search)


@cit_citas_expedientes.route("/cit_citas_expedientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de expedientes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitCitaExpediente.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "expediente" in request.form:
        consulta = consulta.filter(CitCitaExpediente.expediente.like("%" + safe_string(request.form["expediente"]) + "%"))
    registros = consulta.order_by(CitCitaExpediente.expediente.desc()).offset(start).limit(rows_per_page).all()
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
                "cita": {
                    "id": expediente.cita_id,
                    "url": url_for("cit_citas.detail", cita_id=expediente.cita_id),
                    "descripcion": expediente.cita_id,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)
