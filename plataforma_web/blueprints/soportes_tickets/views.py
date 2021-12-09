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


def _get_funcionario_from_current_user():
    """Consultar el funcionario (si es de soporte) a partir del usuario actual"""
    funcionario = Funcionario.query.filter(Funcionario.email == current_user.email).first()
    if funcionario is None:
        return None  # No existe el funcionario
    if funcionario.estatus != "A":
        return None  # No es activo
    if funcionario.en_soportes is False:
        return None  # No es soporte
    return funcionario if funcionario else False


@soportes_tickets.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_tickets.route("/soportes_tickets")
def list_active():
    """Listado de TODOS los Soportes Tickets activos"""
    # Inicializar las tablas a mandar a la plantilla
    abiertos = SoporteTicket.query.filter_by(estado="ABIERTO").filter_by(estatus="A")
    trabajados = SoporteTicket.query.filter_by(estado="TRABAJANDO").filter_by(estatus="A")
    terminados = SoporteTicket.query.filter_by(estado="CERRADO").filter_by(estatus="A")
    cancelados = SoporteTicket.query.filter_by(estado="CANCELADO").filter_by(estatus="A")
    tipo_acceso = None
    # Consultar el funcionario (si es de soporte) a partir del usuario actual
    funcionario = _get_funcionario_from_current_user()
    # Si es administrador
    if current_user.can_admin(MODULO):
        tipo_acceso = "ADMINISTRADOR"
    # Si puede crear tickets y es un funcionario de soporte, mostramos los que ha tomado
    elif current_user.can_insert(MODULO) and funcionario:
        trabajados = trabajados.filter(SoporteTicket.funcionario == funcionario)
        terminados = terminados.filter(SoporteTicket.funcionario == funcionario)
        cancelados = cancelados.filter(SoporteTicket.funcionario == funcionario)
        tipo_acceso = "TECNICO"
    # Si puede crear tickets, mostramos los suyos
    elif current_user.can_insert(MODULO):
        abiertos = abiertos.filter(SoporteTicket.usuario == current_user)
        trabajados = trabajados.filter(SoporteTicket.usuario == current_user)
        terminados = terminados.filter(SoporteTicket.usuario == current_user)
        cancelados = cancelados.filter(SoporteTicket.usuario == current_user)
        tipo_acceso = "USUARIO"
    # De lo contrario, solo puede ver tickets abiertos
    else:
        trabajados = None
        terminados = None
        cancelados = None
        tipo_acceso = "OBSERVADOR"
    # Entregar
    return render_template(
        "soportes_tickets/list.jinja2",
        abiertos=abiertos.order_by(SoporteTicket.id.desc()).limit(100).all(),
        trabajados=trabajados.order_by(SoporteTicket.id.desc()).limit(100).all(),
        terminados=terminados.order_by(SoporteTicket.id.desc()).limit(100).all(),
        cancelados=cancelados.order_by(SoporteTicket.id.desc()).limit(100).all(),
        tipo_acceso=tipo_acceso,
        titulo="Soportes Tickets",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/<int:soporte_ticket_id>")
def detail(soporte_ticket_id):
    """Detalle de un Soporte Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    return render_template("soportes_tickets/detail.jinja2", soporte_ticket=soporte_ticket)


@soportes_tickets.route("/soportes_tickets/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Ticket creado por el usuario"""
    funcionario = Funcionario.query.get_or_404(1) # Funcionario NO DEFINIDO
    form = SoporteTicketNewForm()
    if form.validate_on_submit():
        soporte_ticket = SoporteTicket(
            usuario=current_user,
            soporte_categoria=form.soporte_categoria.data,
            funcionario=funcionario,
            descripcion=safe_string(form.descripcion.data),
            estado="ABIERTO",
            re
        )
        soporte_ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Ticket {soporte_ticket.descripcion}"),
            url=url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("soportes_tickets/new.jinja2", form=form)


@soportes_tickets.route("/soportes_tickets/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_for_usuario(usuario_id):
    """Nuevo Ticket para un usuario especificado"""
    # Consultar el funcionario (si es de soporte) a partir del usuario actual
    funcionario = _get_funcionario_from_current_user()
    if funcionario is None:
        flash("No puede crear tickets para otros usuarios", "warning")
        return redirect(url_for("soportes_tickets.list_active"))

    usuario = Usuario.query.get_or_404(usuario_id)
    form = SoporteTicketNewForm()
    if form.validate_on_submit():
        soporte_ticket = SoporteTicket(
            usuario=usuario,
            soporte_categoria=None,
            funcionario=None,
            descripcion=form.descripcion.data,
            estado="ABIERTO",
        )
        soporte_ticket.save()
        flash(f"Ticket {soporte_ticket.descripcion} guardado.", "success")
        return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))
    return render_template("soportes_tickets/new.jinja2", form=form, usuario=usuario)


@soportes_tickets.route("/soportes_tickets/edicion/<int:soporte_ticket_id>", methods=["GET", "POST"])
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
        flash(f"Ticket {soporte_ticket.id} guardado.", "success")
        return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))
    form.usuario.data = soporte_ticket.usuario.nombre
    form.categoria.data = soporte_ticket.soporte_categoria
    form.tecnico.data = soporte_ticket.funcionario
    form.descripcion.data = soporte_ticket.descripcion
    form.estado.data = soporte_ticket.estado
    form.soluciones.data = soporte_ticket.soluciones
    return render_template("soportes_tickets/edit.jinja2", form=form, soporte_ticket=soporte_ticket)


@soportes_tickets.route("/soportes_tickets/tomar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def take(soporte_ticket_id):
    """Tomar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    funcionario = _get_funcionario_from_current_user()
    if funcionario is False:
        flash(f"Ticket no asignado. No se encuentra el funcionario con el usuario ID: {current_user.id}.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    soporte_ticket.funcionario = funcionario
    soporte_ticket.estado = "TRABAJANDO"
    soporte_ticket.save()
    flash(f"Ticket {soporte_ticket.id} tomado.", "success")
    return redirect(url_for("soportes_tickets.list_active"))


@soportes_tickets.route("/soportes_tickets/cerrar/<int:soporte_ticket_id>", methods=["GET", "POST"])
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
        flash(f"Ticket {soporte_ticket.id} cerrado.", "success")
        return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))
    form.usuario.data = soporte_ticket.usuario.nombre
    form.categoria.data = soporte_ticket.soporte_categoria
    form.tecnico.data = soporte_ticket.funcionario
    form.descripcion.data = soporte_ticket.descripcion
    form.estado.data = soporte_ticket.estado
    form.resolucion.data = datetime.now()
    form.soluciones.data = soporte_ticket.soluciones
    return render_template("soportes_tickets/close.jinja2", form=form, soporte_ticket=soporte_ticket)


@soportes_tickets.route("/soportes_tickets/cancelar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(soporte_ticket_id):
    """Cancelar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    soporte_ticket.estado = "CANCELADO"
    soporte_ticket.save()
    flash(f"Ticket {soporte_ticket.id} cancelado.", "success")
    return redirect(url_for("soportes_tickets.list_active"))


# Delete a ticket

# Recover a ticket
