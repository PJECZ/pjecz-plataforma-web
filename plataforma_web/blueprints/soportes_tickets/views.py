"""
Soportes Tickets, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket

MODULO = "SOPORTES TICKETS"

soportes_tickets = Blueprint("soportes_tickets", __name__, template_folder="templates")


@soportes_tickets.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_tickets.route("/soportes_tickets")
def list_active():
    """Listado de TODOS los Soportes Tickets activos"""
    soportes_tickets_activos = SoporteTicket.query.filter(SoporteTicket.estatus == "A").all()
    return render_template(
        "soportes_tickets/list.jinja2",
        soportes_tickets=soportes_tickets_activos,
        titulo="Soportes Tickets",
        estatus="A",
    )


# List owned tickets


@soportes_tickets.route("/soportes_tickets/<int:soporte_ticket_id>")
def detail(soporte_ticket_id):
    """Detalle de un Soporte Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    return render_template("soportes_tickets/detail.jinja2", soporte_ticket=soporte_ticket)


# Create a new ticket

# Take a open ticket

# Close a ticket

# Cancel a ticket

# Delete a ticket

# Recover a ticket
