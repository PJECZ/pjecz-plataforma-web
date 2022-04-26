"""
Soportes Tickets, vistas
"""
import json
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string, safe_text
from plataforma_web.blueprints.soportes_adjuntos.models import SoporteAdjunto
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.funcionarios_oficinas.models import FuncionarioOficina

from .forms import (
    SoporteTicketNewForm,
    SoporteTicketEditForm,
    SoporteTicketSearchForm,
    SoporteTicketTakeForm,
    SoporteTicketCategorizeForm,
    SoporteTicketCloseForm,
    SoporteTicketDoneForm,
)

MODULO = "SOPORTES TICKETS"

soportes_tickets = Blueprint("soportes_tickets", __name__, template_folder="templates")


def _get_funcionario_if_is_soporte():
    """Consultar el funcionario (si es de soporte) a partir del usuario actual"""
    funcionario = Funcionario.query.filter(Funcionario.email == current_user.email).first()
    if funcionario is None:
        return None  # No existe el funcionario
    if funcionario.estatus != "A":
        return None  # No es activo
    if funcionario.en_soportes is False:
        return None  # No es de soporte
    return funcionario


def _owns_ticket(soporte_ticket: SoporteTicket):
    """Es propietario del ticket, porque lo creo, es de soporte o es administrador"""
    if current_user.can_admin(MODULO):
        return True  # Es administrador
    if _get_funcionario_if_is_soporte():
        return True  # Es de soporte
    if soporte_ticket.usuario == current_user:
        return True  # Es el usuario que creó el ticket
    return False


@soportes_tickets.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_tickets.route("/soportes_tickets")
def list_active():
    """Listado de Tickets: Si es usuario un listado sencillo, si es de soporte los tickets Sin Atender"""
    if _get_funcionario_if_is_soporte() is None:
        return render_template(
            "soportes_tickets/list_user.jinja2",
            titulo="Tickets",
            filtros=json.dumps({"estatus": "A"}),
        )
    return render_template("soportes_tickets/list_open.jinja2")


@soportes_tickets.route("/soportes_tickets/trabajando")
def list_working():
    """Listado de Tickets Trabajando"""
    if _get_funcionario_if_is_soporte() is None:
        return redirect(url_for("soportes_tickets.list_active"))
    return render_template("soportes_tickets/list_working.jinja2")


@soportes_tickets.route("/soportes_tickets/terminados")
def list_done():
    """Listado de Tickets Terminados"""
    if _get_funcionario_if_is_soporte() is None:
        return redirect(url_for("soportes_tickets.list_active"))
    return render_template("soportes_tickets/list_done.jinja2")


@soportes_tickets.route("/soportes_tickets/cerrados")
def list_closed():
    """Listado de Tickets Cerrados"""
    if _get_funcionario_if_is_soporte() is None:
        return redirect(url_for("soportes_tickets.list_active"))
    return render_template("soportes_tickets/list_closed.jinja2")


@soportes_tickets.route("/soportes_tickets/cancelados")
def list_cancel():
    """Listado de Tickets Cancelados"""
    if _get_funcionario_if_is_soporte() is None:
        return redirect(url_for("soportes_tickets.list_active"))
    return render_template("soportes_tickets/list_cancel.jinja2")


@soportes_tickets.route("/soportes_tickets/pendientes")
def list_pending():
    """Listado de Tickets Pendientes"""
    if _get_funcionario_if_is_soporte() is None:
        return redirect(url_for("soportes_tickets.list_active"))
    return render_template("soportes_tickets/list_pending.jinja2")


@soportes_tickets.route("/soportes_tickets/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tickets"""

    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()

    # Consultar y filtrar
    consulta = SoporteTicket.query
    if "estatus" in request.form:
        consulta = consulta.filter(SoporteTicket.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(SoporteTicket.estatus == "A")
    if "creado_desde" in request.form:
        consulta = consulta.filter(SoporteTicket.creado >= request.form["creado_desde"])
    if "creado_hasta" in request.form:
        consulta = consulta.filter(SoporteTicket.creado <= request.form["creado_hasta"])
    if "usuario_id" in request.form:
        consulta = consulta.filter(SoporteTicket.usuario_id == request.form["usuario_id"])
    if "soporte_categoria_id" in request.form:
        consulta = consulta.filter(SoporteTicket.soporte_categoria_id == request.form["soporte_categoria_id"])
    if "oficina_id" in request.form:
        consulta = consulta.join(Usuario).filter(Usuario.oficina_id == request.form["oficina_id"])
    if "funcionario_id" in request.form:
        consulta = consulta.filter(SoporteTicket.funcionario_id == request.form["funcionario_id"])
    if "descripcion" in request.form:
        consulta = consulta.filter(SoporteTicket.descripcion.contains(safe_string(request.form["descripcion"])))
    if "solucion" in request.form:
        consulta = consulta.filter(SoporteTicket.soluciones.contains(safe_string(request.form["solucion"])))
    if "estado" in request.form:
        consulta = consulta.filter(SoporteTicket.estado == safe_string(request.form["estado"]))

    # Obtener el funcionario para saber si es de soporte o no
    funcionario = _get_funcionario_if_is_soporte()

    # Si es funcionario de soporte y se van a separar los tickets POR ATENDER
    if funcionario and "estado" in request.form and "soportes_tickets_abiertos" in request.form and not "buscar" in request.form:
        # Si la tabla es de...
        if request.form["soportes_tickets_abiertos"] == "CERCANOS":
            # Tickets CERCANOS
            oficinas_ids = []
            funcionarios_oficinas = FuncionarioOficina.query.filter(FuncionarioOficina.funcionario == funcionario).filter_by(estatus="A").all()
            for funcionario_oficina in funcionarios_oficinas:
                oficinas_ids.append(funcionario_oficina.oficina_id)
            consulta = consulta.join(Usuario).filter(Usuario.oficina_id.in_(oficinas_ids))
        elif request.form["soportes_tickets_abiertos"] == "CATEGORIZADOS":
            # Tickets CATEGORIZADOS
            roles_ids = []
            for usuario_rol in current_user.usuarios_roles:
                if usuario_rol.estatus == "A":
                    roles_ids.append(usuario_rol.rol_id)
            if len(roles_ids) > 0:
                consulta = consulta.join(SoporteCategoria).filter(SoporteCategoria.rol_id.in_(roles_ids))
        else:
            # Los demas tickets
            roles_ids = []
            for usuario_rol in current_user.usuarios_roles:
                if usuario_rol.estatus == "A":
                    roles_ids.append(usuario_rol.rol_id)
            if len(roles_ids) > 0:
                consulta = consulta.join(SoporteCategoria).filter(SoporteCategoria.rol_id.not_in(roles_ids))
        # Y el orden de los IDs es ascendente, del mas antiguo al mas nuevo
        consulta = consulta.order_by(SoporteTicket.id)
    elif funcionario and "estado" in request.form and "soporte_tickets_trabajando" in request.form and not "buscar" in request.form:
        # Es funcionario de soporte y se van a separar los tickets TRABAJANDO
        if request.form["soporte_tickets_trabajando"] == "MIOS":
            consulta = consulta.filter(SoporteTicket.funcionario == funcionario)
        else:  # TODOS
            consulta = consulta.filter(SoporteTicket.funcionario != funcionario)
        # Y el orden de los IDs es ascendente, del mas antiguo al mas nuevo
        consulta = consulta.order_by(SoporteTicket.id)
    elif funcionario is None:
        # NO es funcionario de soporte, es usuario comun, por lo que SOLO ve sus propios tickets
        consulta = consulta.filter(SoporteTicket.usuario == current_user)
        # Y el orden de los IDs es descendente, del mas nuevo al mas antiguo
        consulta = consulta.order_by(SoporteTicket.id.desc())
    else:
        # El resto de los listados se ordenan por IDs de forma descendente, del mas nuevo al mas antiguo
        consulta = consulta.order_by(SoporteTicket.id.desc())

    # Obtener los registros y el total
    registros = consulta.offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("soportes_tickets.detail", soporte_ticket_id=resultado.id),
                },
                "usuario": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "oficina": {
                    "clave": resultado.usuario.oficina.clave,
                    "nombre": resultado.usuario.oficina.descripcion_corta,
                    "url": url_for("oficinas.detail", oficina_id=resultado.usuario.oficina_id) if current_user.can_view("OFICINAS") else "",
                },
                "categoria": {
                    "nombre": resultado.soporte_categoria.nombre,
                    # Omitimos también que sea usuario común que solicita soportes
                    "url": url_for("soportes_categorias.detail", soporte_categoria_id=resultado.soporte_categoria_id) if (current_user.can_view("SOPORTES CATEGORIAS") and _get_funcionario_if_is_soporte()) else "",
                },
                "descripcion": resultado.descripcion,
                "tecnico": {
                    "nombre": resultado.funcionario.nombre,
                    "url": url_for("funcionarios.detail", funcionario_id=resultado.funcionario_id) if current_user.can_view("FUNCIONARIOS") else "",
                },
                "soluciones": resultado.soluciones if resultado.soluciones else "",
                "estado": resultado.estado,
                "creacion": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                "resolucion": resultado.resolucion.strftime("%Y-%m-%d %H:%M") if resultado.resolucion is not None else "",
            }
        )

    # Entregar JSON
    return output_datatable_json(draw, total, data)


@soportes_tickets.route("/soportes_tickets/<int:soporte_ticket_id>")
def detail(soporte_ticket_id):
    """Detalle de un Soporte Ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if not _owns_ticket(ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    archivos = SoporteAdjunto.query.filter(SoporteAdjunto.soporte_ticket_id == soporte_ticket_id).all()
    inv_custodias = InvCustodia.query.filter(InvCustodia.usuario_id == ticket.usuario_id).order_by(InvCustodia.id.desc()).first()
    inv_equipos = InvEquipo.query.filter(InvEquipo.inv_custodia_id == inv_custodias.usuario_id).all()
    return render_template(
        "soportes_tickets/detail.jinja2",
        soporte_ticket=ticket,
        archivos=archivos,
        inv_custodias=inv_custodias,
        inv_equipos=inv_equipos,
        funcionario=_get_funcionario_if_is_soporte(),
    )


@soportes_tickets.route("/soportes_tickets/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Cualquier usuario puede crear un ticket"""
    tecnico_no_definido = Funcionario.query.get_or_404(1)  # El funcionario con id 1 es NO DEFINIDO
    categoria_no_definida = SoporteCategoria.query.get_or_404(1)  # La categoria con id 1 es NO DEFINIDA
    form = SoporteTicketNewForm()
    if form.validate_on_submit():
        descripcion = safe_text(form.descripcion.data)
        clasificacion = safe_string(form.clasificacion.data)
        if clasificacion != "OTRO":
            descripcion = f"[{clasificacion}] {descripcion}"
        ticket = SoporteTicket(
            funcionario=tecnico_no_definido,
            soporte_categoria=categoria_no_definida,
            usuario=current_user,
            descripcion=descripcion,
            soluciones="",
            estado="SIN ATENDER",
        )
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo ticket {ticket.id}"),
            url=url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = current_user.nombre  # Read only
    form.oficina.data = current_user.oficina.descripcion  # Read only
    return render_template(
        "soportes_tickets/new.jinja2",
        form=form,
        filtros=json.dumps({"estatus": "A", "instrucciones": True}),
    )


@soportes_tickets.route("/soportes_tickets/edicion/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(soporte_ticket_id):
    """Editar un ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if not _owns_ticket(ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede editar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("SIN ATENDER", "TRABAJANDO"):
        flash("No puede editar un ticket que no está SIN ATENDER o TRABAJANDO.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketEditForm()
    if form.validate_on_submit():
        ticket.descripcion = safe_text(form.descripcion.data)
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado el ticket {ticket.id}"),
            url=detalle_url,
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre
    form.descripcion.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria.nombre
    form.tecnico.data = ticket.funcionario.nombre
    form.estado.data = ticket.estado
    return render_template("soportes_tickets/edit.jinja2", form=form, soporte_ticket=ticket)


@soportes_tickets.route("/soportes_tickets/tomar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def take(soporte_ticket_id):
    """Para tomar un ticket este debe estar SIN ATENDER, PENDIENTE o CERRADO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede tomar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("SIN ATENDER", "PENDIENTE", "CERRADO"):
        flash("No puede tomar este ticket porque no esta SIN ATENDER, PENDIENTE o CERRADO.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede tomar el ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketTakeForm()
    if form.validate_on_submit():
        if form.categoria.data.id == 1:
            flash("Por favor eliga una categoría diferente a NO DEFINIDO", "warning")
            return redirect(detalle_url)
        ticket.soporte_categoria = form.categoria.data
        ticket.funcionario = funcionario
        ticket.estado = "TRABAJANDO"
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Tomado el ticket {ticket.id} por {funcionario.nombre}."),
            url=detalle_url,
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre
    form.descripcion.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria
    form.tecnico.data = funcionario.nombre
    return render_template("soportes_tickets/take.jinja2", form=form, soporte_ticket=ticket)


@soportes_tickets.route("/soportes_tickets/soltar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def release(soporte_ticket_id):
    """Para soltar un ticket este debe estar TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede soltar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado != "TRABAJANDO":
        flash("No puede soltar este ticket porque no esta en TRABAJANDO.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede soltar el ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    tecnico_no_definido = Funcionario.query.get_or_404(1)  # El funcionario con id 1 es NO DEFINIDO
    ticket.funcionario = tecnico_no_definido
    ticket.estado = "SIN ATENDER"
    ticket.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Soltado el ticket {ticket.id} por {funcionario.nombre}."),
        url=detalle_url,
    )
    bitacora.save()
    flash(bitacora.descripcion, "success")
    return redirect(bitacora.url)


@soportes_tickets.route("/soportes_tickets/categorizar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def categorize(soporte_ticket_id):
    """Para categorizar un ticket este debe estar SIN ATENDER o TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede categorizar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("SIN ATENDER", "TRABAJANDO"):
        flash("No puede categorizar este ticket porque no está SIN ATENDER o TRABAJANDO.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede categorizar este ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketCategorizeForm()
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
    form.descripcion.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria
    return render_template("soportes_tickets/categorize.jinja2", form=form, soporte_ticket=ticket)


@soportes_tickets.route("/soportes_tickets/terminar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def done(soporte_ticket_id):
    """Para TERMINAR un ticket este debe estar TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede terminar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado != "TRABAJANDO":
        flash("No puede terminar este ticket que no está TRABAJANDO.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede terminar este ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketDoneForm()
    if form.validate_on_submit():
        ticket.estado = "TERMINADO"
        ticket.soluciones = safe_text(form.soluciones.data, to_uppercase=False)
        ticket.resolucion = datetime.now()
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Terminado el ticket {ticket.id}."),
            url=detalle_url,
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre
    form.descripcion.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria.nombre
    form.tecnico.data = ticket.funcionario.nombre
    form.soluciones.data = ticket.soluciones
    return render_template("soportes_tickets/done.jinja2", form=form, soporte_ticket=ticket)


@soportes_tickets.route("/soportes_tickets/cerrar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def close(soporte_ticket_id):
    """Para CERRAR un ticket debe ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede cerrar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("SIN ATENDER", "TRABAJANDO", "PENDIENTE"):
        flash("No puede cerrar este ticket que no está SIN ATENDER, TRABAJANDO o PENDIENTE.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede cerrar este ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketCloseForm()
    if form.validate_on_submit():
        ticket.estado = "CERRADO"
        ticket.soluciones = safe_text(form.soluciones.data, to_uppercase=False)
        ticket.resolucion = datetime.now()
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Cerrado el ticket {ticket.id}."),
            url=detalle_url,
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre
    form.descripcion.data = ticket.descripcion
    form.categoria.data = ticket.soporte_categoria.nombre
    form.tecnico.data = ticket.funcionario.nombre
    form.soluciones.data = ticket.soluciones
    return render_template("soportes_tickets/close.jinja2", form=form, soporte_ticket=ticket)


@soportes_tickets.route("/soportes_tickets/pendiente/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def pending(soporte_ticket_id):
    """Para pasar a un estado de PENDIENTE un ticket debe estar TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede pasar a pendiente un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado != "TRABAJANDO":
        flash("No puede pasar a pendiente este ticket porque no esta TRABAJANDO.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_if_is_soporte()
    if funcionario is None:
        flash("No puede pasar a pendiente este ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    ticket.estado = "PENDIENTE"
    ticket.resolucion = datetime.now()
    ticket.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Pendiente el ticket {ticket.id}."),
        url=detalle_url,
    )
    bitacora.save()
    flash(bitacora.descripcion, "success")
    return redirect(bitacora.url)


@soportes_tickets.route("/soportes_tickets/cancelar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(soporte_ticket_id):
    """Para cancelar un ticket este debe estar SIN ATENDER"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if not _owns_ticket(soporte_ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id)
    if soporte_ticket.estatus != "A":
        flash("No puede cancelar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estado != "SIN ATENDER":
        flash("No puede cancelar este ticket porque no está SIN ATENDER.", "warning")
        return redirect(detalle_url)
    soporte_ticket.estado = "CANCELADO"
    soporte_ticket.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Cancelado el ticket {soporte_ticket.id}."),
        url=detalle_url,
    )
    bitacora.save()
    flash(bitacora.descripcion, "success")
    return redirect(bitacora.url)


@soportes_tickets.route("/soportes_tickets/descancelar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def uncancel(soporte_ticket_id):
    """Para descancelar un ticket este debe estar CANCELADO y ser funcionario de soportes"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id)
    if not _owns_ticket(soporte_ticket):
        flash("No tiene permisos para descancelar un ticket.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estatus != "A":
        flash("No se puede descancelar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estado != "CANCELADO":
        flash("No se puede descancelar este ticket porque no esta CANCELADO.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.funcionario_id == 1:  # Si su funcionario es NO DEFINIDO pasa a SIN ATENDER
        soporte_ticket.estado = "SIN ATENDER"
    else:
        soporte_ticket.estado = "TRABAJANDO"
    soporte_ticket.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"El Ticket {soporte_ticket.id} ha sido descancelado."),
        url=detalle_url,
    )
    bitacora.save()
    flash(bitacora.descripcion, "success")
    return redirect(bitacora.url)


@soportes_tickets.route("/soportes_tickets/eliminar/<int:soporte_ticket_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(soporte_ticket_id):
    """Eliminar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if soporte_ticket.estatus == "A":
        soporte_ticket.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Ticket {soporte_ticket.id}"),
            url=url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))


@soportes_tickets.route("/soportes_tickets/recuperar/<int:soporte_ticket_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(soporte_ticket_id):
    """Recuperar Ticket"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if soporte_ticket.estatus == "B":
        soporte_ticket.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Ticket {soporte_ticket.id}"),
            url=url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))


@soportes_tickets.route("/soportes_tickets/buscar", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def search():
    """Buscar Tickets"""

    # Expulsar si no es de soporte
    funcionario = _get_funcionario_if_is_soporte()
    if not funcionario:
        flash("No tiene permiso para acceder a esa sección", "warning")
        return redirect(url_for("soportes_tickets.list_active"))

    # Recibir formulario
    form_search = SoporteTicketSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []

        # Si se busca por el ID y se encuentra, se redirecciona al detalle
        if form_search.id.data:
            soporte_ticket_id = int(form_search.id.data)
            if soporte_ticket_id != 0:
                soporte_ticket = SoporteTicket.query.get(soporte_ticket_id)
                if soporte_ticket is not None:
                    return redirect(url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id))

        # Si se busca con los demas parametros
        if form_search.creado_desde.data:
            busqueda["creado_desde"] = form_search.creado_desde.data.strftime("%Y-%m-%d 00:00:00")
            titulos.append("fecha de creación desde " + form_search.creado_desde.data.strftime("%Y-%m-%d"))
        if form_search.creado_hasta.data:
            busqueda["creado_hasta"] = form_search.creado_hasta.data.strftime("%Y-%m-%d 24:00:00")
            titulos.append("fecha de creación hasta " + form_search.creado_hasta.data.strftime("%Y-%m-%d"))
        if form_search.descripcion.data:
            descripcion = safe_string(form_search.descripcion.data)
            if descripcion != "":
                busqueda["descripcion"] = descripcion
                titulos.append("descripción " + descripcion)
        if form_search.solucion.data:
            solucion = safe_string(form_search.solucion.data)
            if solucion != "":
                busqueda["solucion"] = solucion
                titulos.append("solución " + solucion)
        if form_search.estado.data:
            estado = safe_string(form_search.estado.data)
            if estado != "":
                busqueda["estado"] = estado
                titulos.append("estado " + estado)

        # Mostrar listado con los resultados
        return render_template(
            "soportes_tickets/list_user.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Tickets con " + ", ".join(titulos),
            estatus="A",
        )

    # Mostrar el formulario de busqueda
    return render_template("soportes_tickets/search.jinja2", form=form_search)
