"""
INV MODELOS, vistas
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
from plataforma_web.blueprints.inv_modelos.models import INVModelos
from plataforma_web.blueprints.inv_modelos.forms import INVModelosForm
from plataforma_web.blueprints.inv_marcas.models import INVMarcas

MODULO = "INV MODELOS"

inv_modelos = Blueprint("inv_modelos", __name__, template_folder="templates")


@inv_modelos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_modelos.route("/inv_modelos")
def list_active():
    """Listado de Modelos activos"""
    # activos = INVModelos.query.filter(INVModelos.estatus == "A").all()
    return render_template(
        "inv_modelos/list.jinja2",
        modelos=INVModelos.query.filter_by(estatus="A").all(),
        titulo="Modelos",
        estatus="A",
    )


@inv_modelos.route("/inv_modelos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Modelos inactivos"""
    # inactivos = INVModelos.query.filter(INVModelos.estatus == "B").all()
    return render_template(
        "inv_modelos/list.jinja2",
        modelos=INVModelos.query.filter_by(estatus="B").all(),
        titulo="Modelos inactivos",
        estatus="B",
    )


@inv_modelos.route("/inv_modelos/<int:modelo_id>")
def detail(modelo_id):
    """Detalle de un Modelos"""
    modelo = INVModelos.query.get_or_404(modelo_id)
    return render_template("inv_modelos/detail.jinja2", modelo=modelo)


# @inv_modelos.route("/inv_modelos/nuevo/", methods=["GET", "POST"])
# @permission_required(MODULO, Permiso.CREAR)
# def new():
#     """Nuevo Modelos"""
#     # marca = INVMarcas.query.get_or_404(marca_id)
#     # if marca.estatus != "A":
#     #     flash("El nombre no esta activo.", "warning")
#     #     return redirect(url_for("inv_marcas.list_active"))
#     # si viene el formulario
#     form = INVModelosForm(CombinedMultiDict((request.files, request.form)))
#     if form.validate_on_submit():
#         es_valido = True
#         # validar la descripcion
#         descripcion = safe_string(form.descripcion.data)
#         if descripcion == "":
#             flash("La descripción es requerida.", "warning")
#             es_valido = False
#         if es_valido:
#             modelo = INVModelos(descripcion=descripcion)
#             modelo.save()
#             flash(f"Modelos {modelo.descripcion} guardado.", "success")
#             return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
#     return render_template("inv_modelos/new.jinja2", form=form)


@inv_modelos.route("/inv_modelos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Modelos"""
    form = INVModelosForm()
    if form.validate_on_submit():
        modelo = INVModelos(descripcion=form.descripcion.data)
        modelo.save()
        flash(f"Modelos {modelo.desceipcion} guardado.", "success")
        return redirect(url_for("inv_modelos.detail", descripcion=modelo.id))
    return render_template("inv_modelos/new.jinja2", form=form)
