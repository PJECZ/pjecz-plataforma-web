"""
Modelos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_marcas.models import INVMarca
from plataforma_web.blueprints.inv_modelos.models import INVModelo

from plataforma_web.blueprints.inv_marcas.forms import INVMarcaForm

MODULO = "INV MARCAS"

inv_marcas = Blueprint("inv_marcas", __name__, template_folder="templates")


@inv_marcas.route("/inv_marcas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Marcas activos"""
    activos = INVMarca.query.filter(INVMarca.estatus == "A").all()
    return render_template(
        "inv_marcas/list.jinja2",
        marcas=activos,
        titulo="Marcas",
        estatus="A",
    )


@inv_marcas.route("/inv_marcas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Marcas inactivos"""
    inactivos = INVMarca.query.filter(INVMarca.estatus == "B").all()
    return render_template(
        "inv_marcas/list.jinja2",
        marcas=inactivos,
        titulo="Marcas inactivos",
        estatus="B",
    )


@inv_marcas.route("/inv_marcas/<int:marca_id>")
def detail(marca_id):
    """Detalle de un Marcas"""
    marca = INVMarca.query.get_or_404(marca_id)
    modelos = INVModelo.query.filter(INVModelo.marca_id == marca_id).all()
    return render_template("inv_marcas/detail.jinja2", marca=marca, modelos=modelos)


@inv_marcas.route("/inv_marcas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Marcas"""
    form = INVMarcaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la marca incorrecto. {str(err)}", "warning")
            validacion = False

        if validacion:
            marca = INVMarca(nombre=safe_string(form.nombre.data))
            marca.save()
            flash(f"Marcas {marca.nombre} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", marca_id=marca.id))
    return render_template("inv_marcas/new.jinja2", form=form)


@inv_marcas.route("/inv_marcas/edicion/<int:marca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(marca_id):
    """Editar Marcas"""
    marca = INVMarca.query.get_or_404(marca_id)
    form = INVMarcaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización de la marca incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            marca.nombre = safe_string(form.nombre.data)
            marca.save()
            flash(f"Marcas {marca.nombre} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", marca_id=marca.id))
    form.nombre.data = marca.nombre
    return render_template("inv_marcas/edit.jinja2", form=form, marca=marca)


def _validar_form(form, same=False):
    if not same:
        nombre_existente = INVMarca.query.filter(INVMarca.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está registrado")
    return True


@inv_marcas.route("/inv_marcas/eliminar/<int:marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(marca_id):
    """Eliminar Marcas"""
    marca = INVMarca.query.get_or_404(marca_id)
    if marca.estatus == "A":
        marca.delete()
        flash(f"Marcas {marca.nombre} eliminado.", "success")
    return redirect(url_for("inv_marcas.detail", marca_id=marca.id))


@inv_marcas.route("/inv_marcas/recuperar/<int:marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(marca_id):
    """Recuperar Marcas"""
    marca = INVMarca.query.get_or_404(marca_id)
    if marca.estatus == "B":
        marca.recover()
        flash(f"Marcas {marca.nombre} recuperado.", "success")
    return redirect(url_for("inv_marcas.detail", marca_id=marca.id))
