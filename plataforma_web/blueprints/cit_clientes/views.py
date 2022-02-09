"""
CITAS Clientes, vistas
"""

from datetime import date, datetime
import json

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib import datatables

from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_clientes.models import CITCliente

from plataforma_web.blueprints.cit_clientes.forms import CITClienteSearchForm

MODULO = "CIT CLIENTES"
RENOVACION_CONTRASENA_DIAS = 360

cit_clientes = Blueprint("cit_clientes", __name__, template_folder="templates")


@cit_clientes.route("/cit_clientes")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Cliente activos"""
    activos = CITCliente.query.filter(CITCliente.estatus == "A").all()
    return render_template(
        "cit_clientes/list.jinja2",
        clientes=activos,
        titulo="Clientes",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )


@cit_clientes.route("/cit_clientes/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Cliente inactivos"""
    inactivos = CITCliente.query.filter(CITCliente.estatus == "B").all()
    return render_template(
        "cit_clientes/list.jinja2",
        clientes=inactivos,
        titulo="Clientes inactivos",
        estatus="B",
        filtros=json.dumps({"estatus": "B"}),
    )


@cit_clientes.route("/cit_clientes/<int:cliente_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(cliente_id):
    """Detalle de un Cliente"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    return render_template("cit_clientes/detail.jinja2", cliente=cliente)

@cit_clientes.route("/cit_clientes/buscar", methods=["GET", "POST"])
def search():
    """Buscar un Cliente"""
    form_search = CITClienteSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []

        # Nombres
        if form_search.nombres.data:
            busqueda["nombres"] = form_search.nombres.data
            titulos.append("nombre " + busqueda["nombres"])
        if form_search.apellido_paterno.data:
            busqueda["apellido_paterno"] = form_search.apellido_paterno.data
            titulos.append("apellido " + busqueda["apellido_paterno"])
        if form_search.apellido_materno.data:
            busqueda["apellido_materno"] = form_search.apellido_materno.data
            titulos.append("apellido " + busqueda["apellido_materno"])
        # CURP
        if form_search.curp.data:
            busqueda["curp"] = safe_string(form_search.curp.data)
            titulos.append("CURP: " + busqueda["curp"])
        # email
        if form_search.email.data:
            busqueda["email"] = form_search.email.data
            titulos.append("email " + busqueda["email"])

        # Mostrar resultados
        return render_template(
            "cit_clientes/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Clientes con " + ", ".join(titulos),
        )

    return render_template("cit_clientes/search.jinja2", form=form_search)


@cit_clientes.route("/cit_clientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de clientes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = CITCliente.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombres" in request.form:
        consulta = consulta.filter(CITCliente.nombres.like("%" + safe_string(request.form["nombres"]) + "%"))
    if "apellido_paterno" in request.form:
        consulta = consulta.filter(CITCliente.apellido_paterno.like("%" + safe_string(request.form["apellido_paterno"]) + "%"))
    if "apellido_materno" in request.form:
        consulta = consulta.filter(CITCliente.apellido_materno.like("%" + safe_string(request.form["apellido_materno"]) + "%"))
    if "curp" in request.form:
        consulta = consulta.filter(CITCliente.curp.like("%" + safe_string(request.form["curp"]) + "%"))
    if "email" in request.form:
        consulta = consulta.filter(CITCliente.email.like("%" + request.form["email"] + "%"))

    registros = consulta.order_by(CITCliente.email.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for cliente in registros:
        data.append(
            {
                "email": {
                    "id": cliente.id,
                    "url": url_for("cit_clientes.detail", cliente_id=cliente.id),
                    "descripcion": cliente.email,
                },
                "nombre_completo": cliente.nombre,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)