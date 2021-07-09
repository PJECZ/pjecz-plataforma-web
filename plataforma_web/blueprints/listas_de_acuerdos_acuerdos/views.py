"""
Listas de Acuerdos Acuerdos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_expediente, safe_message, safe_numero_publicacion, safe_string

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.listas_de_acuerdos_acuerdos.models import ListaDeAcuerdoAcuerdo
from plataforma_web.blueprints.listas_de_acuerdos_acuerdos.forms import ListaDeAcuerdoAcuerdoForm

listas_de_acuerdos_acuerdos = Blueprint("listas_de_acuerdos_acuerdos", __name__, template_folder="templates")

MODULO = "LISTAS DE ACUERDOS"
CONSULTAS_LIMITE = 100


@listas_de_acuerdos_acuerdos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos")
def list_active():
    """Listado de Acuerdos activos"""
    acuerdos_activos = ListaDeAcuerdoAcuerdo.query.filter(ListaDeAcuerdoAcuerdo.estatus == "A").order_by(ListaDeAcuerdoAcuerdo.creado.desc()).limit(CONSULTAS_LIMITE).all()
    return render_template("listas_de_acuerdos_acuerdos/list.jinja2", acuerdos=acuerdos_activos, estatus="A")


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/inactivos")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_inactive():
    """Listado de Acuerdos inactivos"""
    acuerdos_inactivos = ListaDeAcuerdoAcuerdo.query.filter(ListaDeAcuerdoAcuerdo.estatus == "B").order_by(ListaDeAcuerdoAcuerdo.creado.desc()).limit(CONSULTAS_LIMITE).all()
    return render_template("listas_de_acuerdos_acuerdos/list.jinja2", acuerdos=acuerdos_inactivos, estatus="B")


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/<int:lista_de_acuerdo_acuerdo_id>")
def detail(lista_de_acuerdo_acuerdo_id):
    """Detalle de un Acuerdo"""
    acuerdo = ListaDeAcuerdoAcuerdo.query.get_or_404(lista_de_acuerdo_acuerdo_id)
    return render_template("listas_de_acuerdos_acuerdos/detail.jinja2", acuerdo=acuerdo)


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/nuevo/<int:lista_de_acuerdo_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new(lista_de_acuerdo_id):
    """Nuevo Acuerdo"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    form = ListaDeAcuerdoAcuerdoForm()
    if form.validate_on_submit():

        # Validar folio
        try:
            folio = safe_numero_publicacion(form.folio.data)
        except (IndexError, ValueError):
            flash("Folio incorrecto.", "warning")
            return render_template("listas_de_acuerdos_acuerdos/new.jinja2", form=form, lista_de_acuerdo=lista_de_acuerdo)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("Expediente incorrecto.", "warning")
            return render_template("listas_de_acuerdos_acuerdos/new.jinja2", form=form, lista_de_acuerdo=lista_de_acuerdo)

        # Insertar
        acuerdo = ListaDeAcuerdoAcuerdo(
            lista_de_acuerdo=lista_de_acuerdo,
            folio=folio,
            expediente=expediente,
            actor=safe_string(form.actor.data),
            demandado=safe_string(form.demandado.data),
            tipo_acuerdo=safe_string(form.tipo_acuerdo.data),
            tipo_juicio=safe_string(form.tipo_juicio.data),
            referencia=form.referencia.data,
        )
        acuerdo.save()

        # Agregar evento a la bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nuevo acuerdo {acuerdo.referencia} de {acuerdo.lista_de_acuerdo.autoridad.clave} del {acuerdo.lista_de_acuerdo.fecha.strftime('%Y-%m-%d')}."),
            url=url_for("listas_de_acuerdos_acuerdos.detail", lista_de_acuerdo_acuerdo_id=acuerdo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Mostrar formulario
    return render_template("listas_de_acuerdos_acuerdos/new.jinja2", form=form, lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/edicion/<int:lista_de_acuerdo_acuerdo_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(lista_de_acuerdo_acuerdo_id):
    """Editar Acuerdo"""
    acuerdo = ListaDeAcuerdoAcuerdo.query.get_or_404(lista_de_acuerdo_acuerdo_id)
    form = ListaDeAcuerdoAcuerdoForm()
    if form.validate_on_submit():

        # Validar folio
        try:
            acuerdo.folio = safe_numero_publicacion(form.folio.data)
        except (IndexError, ValueError):
            flash("Folio incorrecto.", "warning")
            return render_template("listas_de_acuerdos_acuerdos/edit.jinja2", form=form, acuerdo=acuerdo)

        # Validar expediente
        try:
            acuerdo.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("Expediente incorrecto.", "warning")
            return render_template("listas_de_acuerdos_acuerdos/edit.jinja2", form=form, acuerdo=acuerdo)

        # Insertar
        acuerdo.actor = safe_string(form.actor.data)
        acuerdo.demandado = safe_string(form.demandado.data)
        acuerdo.tipo_acuerdo = safe_string(form.tipo_acuerdo.data)
        acuerdo.tipo_juicio = safe_string(form.tipo_juicio.data)
        acuerdo.referencia = form.referencia.data
        acuerdo.save()

        # Agregar evento a la bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Editado acuerdo {acuerdo.referencia} de {acuerdo.lista_de_acuerdo.autoridad.clave} del {acuerdo.lista_de_acuerdo.fecha.strftime('%Y-%m-%d')}."),
            url=url_for("listas_de_acuerdos_acuerdos.detail", lista_de_acuerdo_acuerdo_id=acuerdo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Mostrar formulario
    form.folio.data = acuerdo.folio
    form.expediente.data = acuerdo.expediente
    form.actor.data = acuerdo.actor
    form.demandado.data = acuerdo.demandado
    form.tipo_acuerdo.data = acuerdo.tipo_acuerdo
    form.tipo_juicio.data = acuerdo.tipo_juicio
    form.referencia.data = acuerdo.referencia
    return render_template("listas_de_acuerdos_acuerdos/edit.jinja2", form=form, acuerdo=acuerdo)


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/eliminar/<int:lista_de_acuerdo_acuerdo_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def delete(lista_de_acuerdo_acuerdo_id):
    """Eliminar Acuerdo"""
    acuerdo = ListaDeAcuerdoAcuerdo.query.get_or_404(lista_de_acuerdo_acuerdo_id)
    if acuerdo.estatus == "A":
        acuerdo.delete()
        flash(f"Acuerdo {acuerdo.referencia} de {acuerdo.lista_de_acuerdo.autoridad.clave} del {acuerdo.lista_de_acuerdo.fecha.strftime('%Y-%m-%d')} eliminado.", "success")
    return redirect(url_for("listas_de_acuerdos_acuerdos.detail", lista_de_acuerdo_acuerdo_id=acuerdo.id))


@listas_de_acuerdos_acuerdos.route("/listas_de_acuerdos_acuerdos/recuperar/<int:lista_de_acuerdo_acuerdo_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def recover(lista_de_acuerdo_acuerdo_id):
    """Recuperar Acuerdo"""
    acuerdo = ListaDeAcuerdoAcuerdo.query.get_or_404(lista_de_acuerdo_acuerdo_id)
    if acuerdo.estatus == "B":
        acuerdo.recover()
        flash(f"Acuerdo {acuerdo.referencia} de {acuerdo.lista_de_acuerdo.autoridad.clave} del {acuerdo.lista_de_acuerdo.fecha.strftime('%Y-%m-%d')} recuperado.", "success")
    return redirect(url_for("listas_de_acuerdos_acuerdos.detail", lista_de_acuerdo_acuerdo_id=acuerdo.id))
