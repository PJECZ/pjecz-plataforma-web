"""
Turnos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib import datatables

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.turnos.models import Turno
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.ventanillas.models import Ventanilla

MODULO = "TURNOS"

turnos = Blueprint("turnos", __name__, template_folder="templates")


@turnos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@turnos.route("/turnos")
def list_active():
    """Listado de Turnos activos"""
    return render_template(
        "turnos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Turnos",
        estatus="A",
    )


@turnos.route("/turnos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de turnos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Turno.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # if "autoridad_id" in request.form:
    #    autoridad = Autoridad.query.get_or_404(request.form["autoridad_id"])
    #    consulta = consulta.filter(Turno.autoridad == autoridad)
    if "ventanilla_id" in request.form:
        ventanilla = Ventanilla.query.get_or_404(request.form["ventanilla_id"])
        consulta = consulta.filter(Turno.ventanilla == ventanilla)
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    if "tipo" in request.form:
        consulta = consulta.filter_by(tipo=request.form["tipo"])
    if "usuario_id" in request.form:
        usuario = Usuario.query.get_or_404(request.form["usuario_id"])
        consulta = consulta.filter(Turno.usuario == usuario)
    registros = consulta.order_by(Turno.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for turno in registros:
        data.append(
            {
                "autoridad_clave": turno.autoridad.clave,
                "ventanilla_numero": turno.ventanilla.numero,
                "detalle": {
                    "numero": turno.numero,
                    "url": url_for("turnos.detail", turno_id=turno.id),
                },
                "estado": turno.estado,
                "tipo": turno.tipo,
                "usuario_email": turno.usuario.email,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@turnos.route("/turnos/<int:turno_id>")
def detail(turno_id):
    """Detalle de un Turno"""
    turno = Turno.query.get_or_404(turno_id)
    return render_template("turnos/detail.jinja2", turno=turno)
