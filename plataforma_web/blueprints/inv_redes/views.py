"""
INV REDES, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_redes.models import INVRedes
from plataforma_web.blueprints.inv_redes.forms import INVRedesForm

MODULO = "INV REDES"

inv_redes = Blueprint("inv_redes", __name__, template_folder="templates")


@inv_redes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_redes.route("/inv_redes")
def list_active():
    """Listado de Redes activos"""
    activos = INVRedes.query.filter(INVRedes.estatus == "A").all()
    return render_template(
        "inv_redes/list.jinja2",
        redes=activos,
        titulo="Redes",
        estatus="A",
    )


@inv_redes.route("/inv_redes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Red inactivos"""
    inactivos = INVRedes.query.filter(INVRedes.estatus == "B").all()
    return render_template(
        "inv_redes/list.jinja2",
        redes=inactivos,
        titulo="Redes inactivos",
        estatus="B",
    )


@inv_redes.route("/inv_redes/<int:red_id>")
def detail(red_id):
    """Detalle de un Red"""
    red = INVRedes.query.get_or_404(red_id)
    return render_template("inv_redes/detail.jinja2", red=red)


@inv_redes.route("/inv_redes/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Red"""
    form = INVRedesForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la red incorrecto. {str(err)}", "warning")
            validacion = False
        if validacion:
            red = INVRedes(nombre=safe_string(form.nombre.data), tipo=safe_string(form.tipo.data))
            red.save()
            flash(f"Red {red.nombre} guardado.", "success")
            return redirect(url_for("inv_redes.detail", red_id=red.id))
    return render_template("inv_redes/new.jinja2", form=form)


@inv_redes.route("/inv_redes/edicion/<int:red_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(red_id):
    """Editar Red"""
    red = INVRedes.query.get_or_404(red_id)
    form = INVRedesForm()
    if form.validate_on_submit():
        red.nombre = safe_string(form.nombre.data)
        red.tipo = safe_string(form.tipo.data)
        red.save()
        flash(f"Red {red.nombre} guardado.", "success")
        return redirect(url_for("inv_redes.detail", red_id=red.id))
    form.nombre.data = red.nombre
    form.tipo.data = red.tipo
    return render_template("inv_redes/edit.jinja2", form=form, red=red)


def _validar_form(form, same=False):
    if not same:
        nombre_existente = INVRedes.query.filter(INVRedes.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está registrado, verifique en el listado de inactivos")
    return True


@inv_redes.route("/inv_redes/eliminar/<int:red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(red_id):
    """Eliminar Red"""
    red = INVRedes.query.get_or_404(red_id)
    if red.estatus == "A":
        red.delete()
        flash(f"Red {red.nombre} eliminado.", "success")
    return redirect(url_for("inv_redes.detail", red_id=red.id))


@inv_redes.route("/inv_redes/recuperar/<int:red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(red_id):
    """Recuperar Red"""
    red = INVRedes.query.get_or_404(red_id)
    if red.estatus == "B":
        red.recover()
        flash(f"Red {red.nombre} recuperado.", "success")
    return redirect(url_for("inv_redes.detail", red_id=red.id))
