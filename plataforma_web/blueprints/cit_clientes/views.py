"""
CITAS Clientes, vistas
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.pwgen import generar_contrasena
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, TOKEN_REGEXP, safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_clientes.models import CITCliente

from plataforma_web.blueprints.cit_clientes.forms import CITClientesForm

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
    )


@cit_clientes.route("/cit_clientes/<int:cliente_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(cliente_id):
    """Detalle de un Cliente"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    return render_template("cit_clientes/detail.jinja2", cliente=cliente)

@cit_clientes.route("/cit_clientes/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo CITAS_Cliente"""
    form = CITClientesForm()
    if form.validate_on_submit():
        if form.contrasena.data == "":
            contrasena = pwd_context.hash(generar_contrasena())
        else:
            contrasena = pwd_context.hash(form.contrasena.data)
        cliente = CITCliente(
            nombres=form.nombres.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            curp=form.curp.data,
            telefono=form.telefono.data,
            email=form.email.data,
            contrasena=contrasena,
            renovacion_fecha=date.today() + datetime.timedelta(days=RENOVACION_CONTRASENA_DIAS),
        )
        cliente.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo cliente {cliente.email}: {cliente.nombre}"),
            url=url_for("cit_clientes.detail", cliente_id=cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("cit_clientes/new.jinja2", form=form)


@cit_clientes.route("/cit_clientes/edicion/<int:cliente_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cliente_id):
    """Editar Cliente, solo al escribir la contraseña se cambia"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    form = CITClientesForm()
    if form.validate_on_submit():
        cliente.nombres = form.nombres.data
        cliente.apellido_paterno = form.apellido_paterno.data
        cliente.apellido_materno = form.apellido_materno.data
        cliente.curp = form.curp.data
        cliente.telefono = form.telefono.data
        cliente.email = form.email.data
        if form.contrasena.data != "":
            cliente.contrasena = pwd_context.hash(form.contrasena.data)
        cliente.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado cliente {cliente.email}: {cliente.nombre}"),
            url=url_for("cit_clientes.detail", cliente_id=cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombres.data = cliente.nombres
    form.apellido_paterno.data = cliente.apellido_paterno
    form.apellido_materno.data = cliente.apellido_materno
    form.curp.data = cliente.curp
    form.telefono.data = cliente.telefono
    form.email.data = cliente.email
    return render_template("cit_clientes/edit.jinja2", form=form, cliente=cliente)


@cit_clientes.route("/cit_clientes/eliminar/<int:cliente_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(cliente_id):
    """Eliminar cliente"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    if cliente.estatus == "A":
        cliente.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado cliente {cliente.email}: {cliente.nombre}"),
            url=url_for("cit_clientes.detail", cliente_id=cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes.detail", cliente_id=cliente_id))


@cit_clientes.route("/cit_clientes/recuperar/<int:cliente_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(cliente_id):
    """Recuperar cliente"""
    cliente = CITCliente.query.get_or_404(cliente_id)
    if cliente.estatus == "B":
        cliente.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado cliente {cliente.email}: {cliente.nombre}"),
            url=url_for("cit_clientes.detail", cliente_id=cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes.detail", cliente_id=cliente_id))
