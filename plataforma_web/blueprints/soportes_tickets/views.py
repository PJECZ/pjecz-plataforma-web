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
from plataforma_web.blueprints.usuarios.models import Usuario

from .forms import SoporteTicketEditForm, SoporteTicketNewForm

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
    soportes_tickets_abiertos = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="ABIERTO").all()
    soportes_tickets_procesando = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="TRABAJANDO").all()
    soportes_tickets_terminados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CERRADO").order_by(SoporteTicket.creado.desc()).limit(50).all()
    soportes_tickets_cancelados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CANCELADO").order_by(SoporteTicket.creado.desc()).limit(50).all()
    return render_template(
        "soportes_tickets/list.jinja2",
        soportes_tickets_abiertos=soportes_tickets_abiertos,
        soportes_tickets_procesando=soportes_tickets_procesando,
        soportes_tickets_terminados=soportes_tickets_terminados,
        soportes_tickets_cancelados=soportes_tickets_cancelados,
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

@soportes_tickets.route('/soportes_tickets/nuevo/<int:usuario_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.CREAR)
def new(usuario_id):
    """Nuevo Ticket creado por el usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = SoporteTicketNewForm()
    if form.validate_on_submit():
        soporte_ticket = SoporteTicket(
            usuario = usuario,
            soporte_categoria = None,
            funcionario = None,
            descripcion=form.descripcion.data,
            estado = "ABIERTO",
        )
        soporte_ticket.save()
        flash(f'Ticket {soporte_ticket.descripcion} guardado.', 'success')
        return redirect(url_for('soportes_tickets.detail', soporte_ticket_id=soporte_ticket.id))
    return render_template('soportes_tickets/new.jinja2', form=form, usuario=usuario)


@soportes_tickets.route('/soportes_tickets/edicion/<int:soporte_ticket_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(soporte_ticket_id):
    """Editar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    form = SoporteTicketEditForm()
    if form.validate_on_submit():
        soporte_ticket.funcionario = form.tecnico.data
        soporte_ticket.soporte_categoria = form.categoria.data
        soporte_ticket.estado = form.estado.data
        soporte_ticket.soluciones = form.soluciones.data
        soporte_ticket.save()
        flash(f'Ticket {soporte_ticket.id} guardado.', 'success')
        return redirect(url_for('soportes_tickets.detail', soporte_ticket_id=soporte_ticket.id))
    form.usuario.data = soporte_ticket.usuario.nombre
    form.categoria.data = soporte_ticket.soporte_categoria
    form.tecnico.data = soporte_ticket.funcionario
    form.descripcion.data = soporte_ticket.descripcion
    form.estado.data = soporte_ticket.estado
    form.soluciones.data = soporte_ticket.soluciones
    return render_template('soportes_tickets/edit.jinja2', form=form, soporte_ticket=soporte_ticket)



# Take a open ticket

# Close a ticket

# Cancel a ticket

# Delete a ticket

# Recover a ticket
