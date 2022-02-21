"""
Soportes Tickets, vistas
"""
import json
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from lib import datatables
from lib.safe_string import safe_message, safe_string, safe_text
from plataforma_web.blueprints.soportes_adjuntos.models import SoporteAdjunto
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket
from plataforma_web.blueprints.usuarios.models import Usuario

from .forms import (
    SoporteTicketNewForm,
    SoporteTicketNewForUsuarioForm,
    SoporteTicketEditForm,
    SoporteTicketSearchForm,
    SoporteTicketTakeForm,
    SoporteTicketCategorizeForm,
    SoporteTicketCloseForm,
    SoporteTicketCancelForm,
)

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
        return None  # No es de soporte
    return funcionario


@soportes_tickets.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_tickets.route("/soportes_tickets")
def list_active():
    """Listado de Tickets"""
    funcionario = _get_funcionario_from_current_user()
    if funcionario:
        return list_soport()
    return list_user()


@soportes_tickets.route("/soportes_tickets/soporte")
def list_soport():
    """Listado de TODOS los Soportes Tickets activos"""
    # Entregar
    return render_template(
        "soportes_tickets/list.jinja2",
        filtros_abiertos_categorizados=json.dumps({"estatus": "A", "estado": "ABIERTO", "soportes_tickets_abiertos": "CATEGORIZADOS"}),
        filtros_abiertos_todos=json.dumps({"estatus": "A", "estado": "ABIERTO", "soportes_tickets_abiertos": "TODOS"}),
        filtros_trabajando_mios=json.dumps({"estatus": "A", "estado": "TRABAJANDO", "soporte_tickets_trabajando": "MIOS"}),
        filtros_trabajando_todos=json.dumps({"estatus": "A", "estado": "TRABAJANDO", "soporte_tickets_trabajando": "TODOS"}),
        titulo="Tickets",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/usuario")
def list_user():
    """Listado de TODOS los Tickets activos para un usuario"""
    # Entregar
    return render_template(
        "soportes_tickets/list_user.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_normal": True}),
        titulo="Tickets",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/terminados")
def list_done():
    """Listado de tickets Terminados"""
    return render_template(
        "soportes_tickets/list_done.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "CERRADO"}),
        titulo="Tickets Terminados",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/cancelados")
def list_cancel():
    """Listado de tickets Cancelados"""
    return render_template(
        "soportes_tickets/list_cancel.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "CANCELADO"}),
        titulo="Tickets Cancelados",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/no_resueltos")
def list_no_resolve():
    """Listado de tickets No resueltos"""
    return render_template(
        "soportes_tickets/list_no_resolve.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "NO RESUELTO"}),
        titulo="Tickets No Resueltos",
        estatus="A",
    )


@soportes_tickets.route("/soportes_tickets/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tickets Terminados"""

    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()

    # Consultar
    consulta = SoporteTicket.query
    if "estatus" in request.form:
        consulta = consulta.filter(SoporteTicket.estatus==request.form["estatus"])
    else:
        consulta = consulta.filter(SoporteTicket.estatus=="A")
    if "fecha_inicio" in request.form:
        consulta = consulta.filter(SoporteTicket.creado >= request.form["fecha_inicio"])
    if "fecha_termino" in request.form:
        consulta = consulta.filter(SoporteTicket.creado <= request.form["fecha_termino"])
    if "categoria" in request.form:
        consulta = consulta.filter(SoporteTicket.soporte_categoria_id == request.form["categoria"])
    #if "oficina" in request.form:
    #    consulta = consulta.filter(SoporteTicket.soporte_categoria == request.form["oficina"])
    if "descripcion" in request.form:
        consulta = consulta.filter(SoporteTicket.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))
    if "solucion" in request.form:
        consulta = consulta.filter(SoporteTicket.soluciones.like("%" + safe_string(request.form["solucion"]) + "%"))

    if "usuario_normal" in request.form:
        consulta = consulta.filter(SoporteTicket.usuario == current_user).order_by(SoporteTicket.id.desc())
    else:
        if "estado" in request.form:
            consulta = consulta.filter(SoporteTicket.estado==request.form["estado"])
            if request.form["estado"] in ("TERMINADO", "CANCELADO", "NO RESUELTO", "CERRADO"):
                consulta = consulta.order_by(SoporteTicket.id.desc())
            else:
                consulta = consulta.order_by(SoporteTicket.id.asc())

    if "soportes_tickets_abiertos" in request.form:
        # Extraemos los roles del usuario
        current_user_roles_id = []
        for usuario_rol in current_user.usuarios_roles:
            if usuario_rol.estatus == "A":
                current_user_roles_id.append(usuario_rol.rol.id)
        if request.form["soportes_tickets_abiertos"] == "CATEGORIZADOS":
            consulta = consulta.join(SoporteCategoria).filter(SoporteCategoria.rol_id.in_(current_user_roles_id))
        else: # TODOS
            consulta = consulta.join(SoporteCategoria).filter(SoporteCategoria.rol_id.not_in(current_user_roles_id))

    if "soporte_tickets_trabajando" in request.form:
        funcionario = _get_funcionario_from_current_user()
        if request.form["soporte_tickets_trabajando"] == "MIOS":
            consulta = consulta.filter(SoporteTicket.funcionario == funcionario)
        else: # TODOS
            consulta = consulta.filter(SoporteTicket.funcionario != funcionario)

    if consulta is None:
        return datatables.output(draw, 0, [])
    else:
        registros = consulta.offset(start).limit(rows_per_page).all()
        total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        if resultado.resolucion is None:
            resolucion = "—"
        else:
            resolucion = resultado.resolucion.strftime("%Y-%m-%d %H:%M")
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("soportes_tickets.detail", soporte_ticket_id=resultado.id),
                },
                "usuario": resultado.usuario.nombre,
                "oficina": {
                    "clave": resultado.usuario.oficina.clave,
                    "nombre": resultado.usuario.oficina.descripcion_corta,
                },
                "categoria": resultado.soporte_categoria.nombre,
                "descripcion": resultado.descripcion,
                "tecnico": resultado.funcionario.nombre,
                "soluciones": resultado.soluciones,
                "estado": resultado.estado,
                "inicio": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                "termino": resolucion,
            }
        )

    # Entregar JSON
    return datatables.output(draw, total, data)


@soportes_tickets.route("/soportes_tickets/<int:soporte_ticket_id>")
def detail(soporte_ticket_id):
    """Detalle de un Soporte Ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if _expulsar_usuario(ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))

    archivos = SoporteAdjunto.query.filter(SoporteAdjunto.soporte_ticket_id == soporte_ticket_id).all()
    return render_template(
        "soportes_tickets/detail.jinja2",
        soporte_ticket=ticket,
        archivos=archivos,
        funcionario=_get_funcionario_from_current_user(),
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
            descripcion=f"[{clasificacion}] {descripcion}"
        ticket = SoporteTicket(
            funcionario=tecnico_no_definido,
            soporte_categoria=categoria_no_definida,
            usuario=current_user,
            descripcion=descripcion,
            soluciones="",
            estado="ABIERTO",
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
    form.usuario.data = current_user.nombre
    return render_template(
        "soportes_tickets/new.jinja2",
        form=form,
        filtros=json.dumps({"estatus": "A", "instrucciones": True}),
    )


@soportes_tickets.route("/soportes_tickets/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def new_for_usuario(usuario_id):
    """Solo un administrador puede crear un ticket para otro usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus != "A":
        flash("El usuario esta eliminado", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    tecnico = _get_funcionario_from_current_user()
    if tecnico is None:
        flash("No puede crear tickets; necesita ser funcionario de soporte para hacerlo", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    form = SoporteTicketNewForUsuarioForm()
    if form.validate_on_submit():
        ticket = SoporteTicket(
            funcionario=tecnico,
            soporte_categoria=form.categoria.data,
            usuario=usuario,
            descripcion=safe_text(form.descripcion.data),
            estado="ABIERTO",
            resolucion="",
            soluciones="",
        )
        ticket.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo ticket {ticket.id} por {tecnico.nombre}"),
            url=url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario.data = usuario.nombre
    return render_template("soportes_tickets/new_for_usuario.jinja2", form=form, usuario=usuario)


def _expulsar_usuario(ticket):
    """Expulsar al usuario normal de un ticket"""
    # Consultar el funcionario (si es de soporte) a partir del usuario actual
    funcionario = _get_funcionario_from_current_user()
    # Si es administrador
    if current_user.can_admin(MODULO):
        return False
    # Si puede crear tickets y es un funcionario de soporte, mostramos los que ha tomado
    elif current_user.can_insert(MODULO) and funcionario:
        return False
    # Si puede crear tickets, mostramos los suyos
    elif current_user.can_insert(MODULO):
        if ticket.usuario == current_user:
            return False
    # De lo contrario, solo puede ver tickets abiertos
    return True



@soportes_tickets.route("/soportes_tickets/edicion/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(soporte_ticket_id):
    """Editar un ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if _expulsar_usuario(ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))

    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede editar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("ABIERTO", "TRABAJANDO"):
        flash("No puede editar un ticket que no está abierto o trabajando.", "warning")
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
    """Para tomar un ticket este debe estar ABIERTO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede tomar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado != "ABIERTO":
        flash("No puede tomar un ticket que no está abierto.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
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
    if ticket.estado == "ABIERTO":
        flash("No puede soltar un ticket que está abierto.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
    if funcionario is None:
        flash("No puede soltar el ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    tecnico_no_definido = Funcionario.query.get_or_404(1)  # El funcionario con id 1 es NO DEFINIDO
    ticket.funcionario = tecnico_no_definido
    ticket.estado = "ABIERTO"
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
    """Para categorizar un ticket este debe estar ABIERTO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede categorizar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("ABIERTO", "TRABAJANDO"):
        flash("No puede categorizar un ticket que no está abierto o trabajando.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
    if funcionario is None:
        flash("No puede tomar el ticket porque no es funcionario de soporte.", "warning")
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


@soportes_tickets.route("/soportes_tickets/cerrar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def close(soporte_ticket_id):
    """Para cerrar un ticket este debe estar TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede cerrar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado != "TRABAJANDO":
        flash("No puede cerrar un ticket que no está trabajando.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
    if funcionario is None:
        flash("No puede cerrar el ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    form = SoporteTicketCloseForm()
    if form.validate_on_submit():
        ticket.estado = "CERRADO"
        ticket.soluciones = safe_text(form.soluciones.data)
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


@soportes_tickets.route("/soportes_tickets/no_resolve/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def no_resolve(soporte_ticket_id):
    """Para 'no resuelto' un ticket este debe estar TRABAJANDO y ser funcionario de soportes"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede pasar a no resuelto un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado not in ("ABIERTO", "TRABAJANDO"):
        flash("No puede pasar a no resuelto un ticket que no está abierto o trabajando.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
    if funcionario is None:
        flash("No puede pasar a no resuelto el ticket porque no es funcionario de soporte.", "warning")
        return redirect(detalle_url)
    ticket.estado = "NO RESUELTO"
    ticket.resolucion = datetime.now()
    ticket.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"No resuelto el ticket {ticket.id}."),
        url=detalle_url,
    )
    bitacora.save()
    flash(bitacora.descripcion, "success")
    return redirect(bitacora.url)


@soportes_tickets.route("/soportes_tickets/cancelar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(soporte_ticket_id):
    """Para cancelar un ticket este debe estar ABIERTO o TRABAJANDO y ser funcionario de soportes"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    if _expulsar_usuario(soporte_ticket):
        flash("No tiene permisos para ver ese ticket.", "warning")
        return redirect(url_for("soportes_tickets.list_active"))
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id)
    if soporte_ticket.estatus != "A":
        flash("No puede cancelar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estado not in ("ABIERTO", "TRABAJANDO"):
        flash("No puede cancelar un ticket que no está abierto o trabajando.", "warning")
        return redirect(detalle_url)

    form = SoporteTicketCancelForm()
    if form.validate_on_submit():
        soporte_ticket.estado = "CANCELADO"
        soporte_ticket.soluciones = safe_string(form.soluciones.data)
        soporte_ticket.resolucion = datetime.now()
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
    form.usuario.data = soporte_ticket.usuario.nombre
    form.descripcion.data = soporte_ticket.descripcion
    form.categoria.data = soporte_ticket.soporte_categoria.nombre
    form.tecnico.data = soporte_ticket.funcionario.nombre
    form.soluciones.data = soporte_ticket.soluciones
    return render_template("soportes_tickets/cancel.jinja2", form=form, soporte_ticket=soporte_ticket)


@soportes_tickets.route("/soportes_tickets/descancelar/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def uncancel(soporte_ticket_id):
    """Para descancelar un ticket este debe estar CANCELADO y ser funcionario de soportes"""
    soporte_ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=soporte_ticket.id)
    if _expulsar_usuario(soporte_ticket) or soporte_ticket.usuario == current_user:
        flash("No tiene permisos para descancelar un ticket.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estatus != "A":
        flash("No se puede descancelar un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.estado != "CANCELADO":
        flash("No se puede descancelar un ticket que no este en estado de CANCELADO.", "warning")
        return redirect(detalle_url)
    if soporte_ticket.funcionario_id == 1:  # Si su funcionario es NO DEFINIDO pasa a ABIERTO
        soporte_ticket.estado = "ABIERTO"
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
def search():
    """Buscar Tickets"""
    form_search = SoporteTicketSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.fecha_inicio.data:
            busqueda["fecha_inicio"] = form_search.fecha_inicio.data.strftime("%Y-%m-%d 00:00:00")
            titulos.append("fecha de inicio " + busqueda["fecha_inicio"])
        if form_search.fecha_termino.data:
            busqueda["fecha_termino"] = form_search.fecha_termino.data.strftime("%Y-%m-%d 24:00:00")
            titulos.append("fecha de termino " + busqueda["fecha_termino"])
        if form_search.categoria.data:
            flash(f"Categoria {form_search.categoria.data}", "info")
            categoria = "2"#safe_string(form_search.categoria.data)
            if categoria != "":
                busqueda["categoria"] = categoria
                titulos.append("categoria " + categoria)
        if form_search.oficina.data:
            oficina = safe_string(form_search.oficina.data)
            if oficina != "":
                busqueda["oficina"] = oficina
                titulos.append("oficina " + oficina)
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
        return render_template(
            "soportes_tickets/list_search.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Tickets con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("soportes_tickets/search.jinja2", form=form_search)
