"""
Categorias, vistas
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
from plataforma_web.blueprints.inv_categorias.models import INVCategoria

from plataforma_web.blueprints.inv_categorias.forms import INVCategoriaForm

MODULO = "INV CATEGORIAS"

inv_categorias = Blueprint("inv_categorias", __name__, template_folder="templates")


@inv_categorias.route("/inv_categorias")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Categorias activos"""
    activos = INVCategoria.query.filter(INVCategoria.estatus == "A").all()
    return render_template(
        "inv_categorias/list.jinja2",
        categorias=activos,
        titulo="Categorias",
        estatus="A",
    )


@inv_categorias.route("/inv_categorias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Categorias inactivos"""
    inactivos = INVCategoria.query.filter(INVCategoria.estatus == "B").all()
    return render_template(
        "inv_categorias/list.jinja2",
        categorias=inactivos,
        titulo="Categorias inactivos",
        estatus="B",
    )


@inv_categorias.route("/inv_categorias/<int:categoria_id>")
def detail(categoria_id):
    """Detalle de un Categorias"""
    categoria = INVCategoria.query.get_or_404(categoria_id)
    return render_template("inv_categorias/detail.jinja2", categoria=categoria)


@inv_categorias.route("/inv_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Categoria"""
    form = INVCategoriaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la categoria incorrecto. {str(err)}", "warning")
            validacion = False

        if validacion:
            categoria = INVCategoria(nombre=safe_string(form.nombre.data))
            categoria.save()
            flash(f"Categorias {categoria.nombre} guardado.", "success")
            return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))
    return render_template("inv_categorias/new.jinja2", form=form)


@inv_categorias.route("/inv_categorias/edicion/<int:categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(categoria_id):
    """Editar Categoria"""
    categoria = INVCategoria.query.get_or_404(categoria_id)
    form = INVCategoriaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización de la categoria incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            categoria.nombre = safe_string(form.nombre.data)
            categoria.save()
            flash(f"Categorias {categoria.nombre} guardado.", "success")
            return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))
    form.nombre.data = categoria.nombre
    return render_template("inv_categorias/edit.jinja2", form=form, categoria=categoria)


def _validar_form(form, same=False):
    if not same:
        nombre_existente = INVCategoria.query.filter(INVCategoria.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está regsitrado.")
    return True


@inv_categorias.route("/inv_categorias/eliminar/<int:categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(categoria_id):
    """Eliminar Categorias"""
    categoria = INVCategoria.query.get_or_404(categoria_id)
    if categoria.estatus == "A":
        categoria.delete()
        flash(f"Categorias {categoria.nombre} eliminado.", "success")
    return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))


@inv_categorias.route("/inv_categorias/recuperar/<int:categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(categoria_id):
    """Recuperar Categorias"""
    categoria = INVCategoria.query.get_or_404(categoria_id)
    if categoria.estatus == "B":
        categoria.recover()
        flash(f"Categorias {categoria.nombre} recuperado.", "success")
    return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))
