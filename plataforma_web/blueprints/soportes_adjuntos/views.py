"""
Soportes Adjuntos, vistas
"""
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.soportes_adjuntos.models import SoporteAdjunto
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.soportes_adjuntos.forms import SoporteAdjuntoNewForm

MODULO = "SOPORTES ADJUNTOS"

soportes_adjuntos = Blueprint("soportes_adjuntos", __name__, template_folder="templates")


def _get_funcionario_from_current_user():
    """Consultar el funcionario (si es de soporte) a partir del usuario actual"""
    funcionario = Funcionario.query.filter(Funcionario.email == current_user.email).first()
    if funcionario is None:
        return None  # No existe el funcionario
    if funcionario.estatus != "A":
        return None  # No es activo
    if funcionario.en_soportes is False:
        return None  # No es de soporte
    return funcionario


@soportes_adjuntos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_adjuntos.route("/soportes_adjuntos/nuevo/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(soporte_ticket_id):
    """Adjuntar Archivos al Ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    #archivo = SoporteTicketFile
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede adjuntar un archivo a un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado is ("ABIERTO", "TRABAJANDO"):
        flash("No puede adjuntar un archivo a un ticket que no está abierto o trabajando.", "warning")
        return redirect(detalle_url)
    form = SoporteAdjuntoNewForm()
    if form.validate_on_submit():
        ticket.soporte_categoria = form.categoria.data
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Categorizado el ticket {ticket.id} a {ticket.soporte_categoria.nombre} por {funcionario.nombre}."),
            url=detalle_url,
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre
    form.problema.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria.nombre
    return render_template("soportes_adjuntos/new.jinja2", form=form, soporte_ticket=ticket)
