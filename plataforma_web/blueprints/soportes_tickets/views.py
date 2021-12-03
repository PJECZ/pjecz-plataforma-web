"""
Soportes Tickets, vistas
"""
from datetime import datetime
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
from plataforma_web.blueprints.funcionarios.models import Funcionario

from .forms import SoporteTicketEditForm, SoporteTicketNewForm, SoporteTicketCloseForm

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
    soportes_tickets_abiertos = []
    soportes_tickets_procesando = []
    soportes_tickets_terminados = []
    soportes_tickets_cancelados = []
    tipo_acceso = None

    # Query para administradores
    if current_user.can_admin(MODULO):
        soportes_tickets_abiertos = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="ABIERTO").all()
        soportes_tickets_procesando = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="TRABAJANDO").all()
        soportes_tickets_terminados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CERRADO").order_by(SoporteTicket.creado.desc()).limit(50).all()
        soportes_tickets_cancelados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CANCELADO").order_by(SoporteTicket.creado.desc()).limit(50).all()
        tipo_acceso = "ADMIN"

    # Query para Técnicos
    elif current_user.can_edit(MODULO):
        soportes_tickets_abiertos = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="ABIERTO").all()
        funcionario = _current_user_in_funcionario()
        if funcionario is False:
            flash(f'No se encuentra el funcionario con el usuario ID: {current_user.id}.', 'warning')
        soportes_tickets_procesando = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="TRABAJANDO").filter(SoporteTicket.funcionario == funcionario).all()
        soportes_tickets_terminados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CERRADO").order_by(SoporteTicket.creado.desc()).filter(SoporteTicket.funcionario == funcionario).limit(50).all()
        soportes_tickets_cancelados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CANCELADO").order_by(SoporteTicket.creado.desc()).filter(SoporteTicket.funcionario == funcionario).limit(50).all()
        tipo_acceso = "TECNICO"

    # Query para Usuarios
    elif current_user.can_view(MODULO):
        soportes_tickets_abiertos = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="ABIERTO").all()
        soportes_tickets_procesando = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="TRABAJANDO").filter(SoporteTicket.usuario_id == current_user.id).all()
        soportes_tickets_terminados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CERRADO").order_by(SoporteTicket.creado.desc()).filter(SoporteTicket.usuario_id == current_user.id).limit(50).all()
        soportes_tickets_cancelados = SoporteTicket.query.filter(SoporteTicket.estatus == "A").filter(SoporteTicket.estado=="CANCELADO").order_by(SoporteTicket.creado.desc()).filter(SoporteTicket.usuario_id == current_user.id).limit(50).all()
        tipo_acceso = "USUARIO"

    else:
        return redirect(url_for(''))

    # Query para Usuarios
    return render_template(
        "soportes_tickets/list.jinja2",
        soportes_tickets_abiertos=soportes_tickets_abiertos,
        soportes_tickets_procesando=soportes_tickets_procesando,
        soportes_tickets_terminados=soportes_tickets_terminados,
        soportes_tickets_cancelados=soportes_tickets_cancelados,
        tipo_acceso=tipo_acceso,
        titulo="Soportes Tickets",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/<int:soporte_ticket_id>")
def detail(soporte_ticket_id):
    """Detalle de un Soporte Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    return render_template("soportes_tickets/detail.jinja2", soporte_ticket=soporte_ticket)


# Create a new ticket

@soportes_tickets.route('/soportes_tickets/nuevo/<int:usuario_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.VER)
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


@soportes_tickets.route('/soportes_tickets/tomar/<int:soporte_ticket_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def take(soporte_ticket_id):
    """Tomar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    funcionario = _current_user_in_funcionario()
    if funcionario is False:
        flash(f'Ticket no asignado. No se encuentra el funcionario con el usuario ID: {current_user.id}.', 'warning')
        return redirect(url_for('soportes_tickets.list_active'))
    soporte_ticket.funcionario = funcionario
    soporte_ticket.estado = "TRABAJANDO"
    soporte_ticket.save()
    flash(f'Ticket {soporte_ticket.id} tomado.', 'success')
    return redirect(url_for('soportes_tickets.list_active'))


@soportes_tickets.route('/soportes_tickets/cerrar/<int:soporte_ticket_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def closes(soporte_ticket_id):
    """Cerrar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    form = SoporteTicketCloseForm()
    if form.validate_on_submit():
        soporte_ticket.estado = "CERRADO"
        soporte_ticket.soluciones = form.soluciones.data
        soporte_ticket.resolucion = form.resolucion.data
        soporte_ticket.save()
        flash(f'Ticket {soporte_ticket.id} cerrado.', 'success')
        return redirect(url_for('soportes_tickets.detail', soporte_ticket_id=soporte_ticket.id))
    form.usuario.data = soporte_ticket.usuario.nombre
    form.categoria.data = soporte_ticket.soporte_categoria
    form.tecnico.data = soporte_ticket.funcionario
    form.descripcion.data = soporte_ticket.descripcion
    form.estado.data = soporte_ticket.estado
    form.resolucion.data = datetime.now()
    form.soluciones.data = soporte_ticket.soluciones
    return render_template('soportes_tickets/close.jinja2', form=form, soporte_ticket=soporte_ticket)


@soportes_tickets.route('/soportes_tickets/cancelar/<int:soporte_ticket_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(soporte_ticket_id):
    """Cancelar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    soporte_ticket.estado = "CANCELADO"
    soporte_ticket.save()
    flash(f'Ticket {soporte_ticket.id} cancelado.', 'success')
    return redirect(url_for('soportes_tickets.list_active'))

# Delete a ticket

# Recover a ticket

def _current_user_in_funcionario():
    usuario = Usuario.query.get_or_404(current_user.id)
    funcionario = Funcionario.query.filter(Funcionario.email == usuario.email).first()
    return funcionario if funcionario else False
