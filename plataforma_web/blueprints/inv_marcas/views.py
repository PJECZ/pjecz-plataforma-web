"""
Inventarios Modelos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_marcas.forms import InvMarcaForm
from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV MARCAS"

inv_marcas = Blueprint("inv_marcas", __name__, template_folder="templates")


@inv_marcas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_marcas.route("/inv_marcas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV MARCAS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvMarca.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(InvMarca.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_marcas.detail", inv_marca_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_marcas.route("/inv_marcas")
def list_active():
    """Listado de INV MARCAS activos"""
    return render_template(
        "inv_marcas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Marcas",
        estatus="A",
    )


@inv_marcas.route("/inv_marcas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de INV MARCAS inactivos"""
    return render_template(
        "inv_marcas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Marcas inactivos",
        estatus="B",
    )


@inv_marcas.route("/inv_marcas/<int:inv_marca_id>")
def detail(inv_marca_id):
    """Detalle de un Marcas"""
    inv_marca = InvMarca.query.get_or_404(inv_marca_id)
    return render_template("inv_marcas/detail.jinja2", inv_marca=inv_marca)


@inv_marcas.route("/inv_marcas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Marcas"""
    form = InvMarcaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data, save_enie=True)
        inv_marca_existente = InvMarca.query.filter_by(nombre=nombre).first()
        if inv_marca_existente:
            flash("Ya existe una marca con ese nombre.", "warning")
            es_valido = False
        # Si es valido insertar
        if es_valido:
            inv_marca = InvMarca(nombre=nombre)
            inv_marca.save()
            flash(f"Marcas {inv_marca.nombre} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", inv_marca_id=inv_marca.id))
    return render_template("inv_marcas/new.jinja2", form=form)


@inv_marcas.route("/inv_marcas/edicion/<int:inv_marca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_marca_id):
    """Editar Marcas"""
    inv_marca = InvMarca.query.get_or_404(inv_marca_id)
    form = InvMarcaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data, save_enie=True)
        inv_marca_existente = InvMarca.query.filter_by(nombre=nombre).first()
        if inv_marca_existente and inv_marca_existente.id != inv_marca.id:
            flash("Ya existe una marca con ese nombre.", "warning")
            es_valido = False
        # Si es valido actualizar
        if es_valido:
            inv_marca.nombre = nombre
            inv_marca.save()
            flash(f"Marcas {inv_marca.nombre} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", inv_marca_id=inv_marca.id))
    form.nombre.data = inv_marca.nombre
    return render_template("inv_marcas/edit.jinja2", form=form, inv_marca=inv_marca)


@inv_marcas.route("/inv_marcas/eliminar/<int:inv_marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_marca_id):
    """Eliminar Marcas"""
    inv_marca = InvMarca.query.get_or_404(inv_marca_id)
    if inv_marca.estatus == "A":
        inv_marca.delete()
        flash(f"Marcas {inv_marca.nombre} eliminado.", "success")
    return redirect(url_for("inv_marcas.detail", inv_marca_id=inv_marca.id))


@inv_marcas.route("/inv_marcas/recuperar/<int:inv_marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_marca_id):
    """Recuperar Marcas"""
    inv_marca = InvMarca.query.get_or_404(inv_marca_id)
    if inv_marca.estatus == "B":
        inv_marca.recover()
        flash(f"Marcas {inv_marca.nombre} recuperado.", "success")
    return redirect(url_for("inv_marcas.detail", inv_marca_id=inv_marca.id))
