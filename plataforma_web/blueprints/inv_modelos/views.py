"""
Inventarios Modelos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.inv_modelos.forms import InvModeloForm, InvModeloEditForm
from plataforma_web.blueprints.inv_modelos.models import InvModelo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV MODELOS"

inv_modelos = Blueprint("inv_modelos", __name__, template_folder="templates")


@inv_modelos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_modelos.route("/inv_modelos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV MODELOS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvModelo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "inv_marca_id" in request.form:
        marca = InvMarca.query.get(request.form["inv_marca_id"])
        if marca:
            consulta = consulta.filter(InvModelo.inv_marca == marca)
    registros = consulta.order_by(InvModelo.descripcion).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("inv_modelos.detail", inv_modelo_id=resultado.id),
                },
                "marca": {
                    "nombre": resultado.inv_marca.nombre,
                    "url": url_for("inv_marcas.detail", inv_marca_id=resultado.inv_marca_id) if current_user.can_view("INV MARCAS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_modelos.route("/inv_modelos")
def list_active():
    """Listado de INV MODELOS activos"""
    return render_template(
        "inv_modelos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Modelos",
        estatus="A",
    )


@inv_modelos.route("/inv_modelos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de INV MODELOS inactivos"""
    return render_template(
        "inv_modelos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Modelos inactivos",
        estatus="B",
    )


@inv_modelos.route("/inv_modelos/<int:inv_modelo_id>")
def detail(inv_modelo_id):
    """Detalle de un Modelos"""
    inv_modelo = InvModelo.query.get_or_404(inv_modelo_id)
    return render_template("inv_modelos/detail.jinja2", inv_modelo=inv_modelo)


@inv_modelos.route("/inv_modelos/nuevo/<int:inv_marca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(inv_marca_id):
    """Nuevo Modelos"""
    inv_marca = InvMarca.query.get_or_404(inv_marca_id)
    form = InvModeloForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista esa descripción
        descripcion = safe_string(form.descripcion.data)
        inv_modelo_existente = InvModelo.query.filter_by(descripcion=descripcion).first()
        if inv_modelo_existente:
            flash("Ya existe un modelo con esa descripción.", "warning")
            es_valido = False
        # Si es valido insertar
        if es_valido:
            modelo = InvModelo(
                inv_marca=inv_marca,
                descripcion=descripcion,
            )
            modelo.save()
            flash(f"Modelos {modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", inv_marca_id=inv_marca_id))
    form.nombre.data = inv_marca.nombre  # Read only
    return render_template("inv_modelos/new.jinja2", form=form, inv_marca=inv_marca)


@inv_modelos.route("/inv_modelos/edicion/<int:inv_modelo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_modelo_id):
    """Editar Modelo"""
    inv_modelo = InvModelo.query.get_or_404(inv_modelo_id)
    form = InvModeloEditForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista esa descripción
        descripcion = safe_string(form.descripcion.data)
        inv_modelo_existente = InvModelo.query.filter_by(descripcion=descripcion).first()
        if inv_modelo_existente and inv_modelo_existente.id != inv_modelo.id:
            flash("Ya existe un modelo con esa descripción.", "warning")
            es_valido = False
        # Si es valido actualizar
        if es_valido:
            inv_modelo.descripcion = safe_string(form.descripcion.data)
            inv_modelo.save()
            flash(f"Modelo {inv_modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_modelos.detail", inv_modelo_id=inv_modelo.id))
    form.nombre.data = inv_modelo.inv_marca.nombre  # Read only
    form.descripcion.data = inv_modelo.descripcion
    return render_template("inv_modelos/edit.jinja2", form=form, inv_modelo=inv_modelo)


@inv_modelos.route("/inv_modelos/eliminar/<int:inv_modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_modelo_id):
    """Eliminar Modelo"""
    inv_modelo = InvModelo.query.get_or_404(inv_modelo_id)
    if inv_modelo.estatus == "A":
        inv_modelo.delete()
        flash(f"Modelo { inv_modelo.descripcion} eliminado.", "success")
    return redirect(url_for("inv_modelos.detail", inv_modelo_id=inv_modelo.id))


@inv_modelos.route("/inv_modelos/recuperar/<int:inv_modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_modelo_id):
    """Recuperar Modelo"""
    inv_modelo = InvModelo.query.get_or_404(inv_modelo_id)
    if inv_modelo.estatus == "B":
        inv_modelo.recover()
        flash(f"Modelo {inv_modelo.descripcion} recuperado.", "success")
    return redirect(url_for("inv_modelos.detail", inv_modelo_id=inv_modelo.id))
