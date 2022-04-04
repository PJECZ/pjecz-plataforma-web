"""
Inventarios Categorías, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_categorias.forms import InvCategoriaForm
from plataforma_web.blueprints.inv_categorias.models import InvCategoria
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV CATEGORIAS"

inv_categorias = Blueprint("inv_categorias", __name__, template_folder="templates")


@inv_categorias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_categorias.route("/inv_categorias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV CATEGORIAS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvCategoria.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(InvCategoria.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_categorias.detail", inv_categoria_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_categorias.route("/inv_categorias")
def list_active():
    """Listado de INV CATEGORIAS activos"""
    return render_template(
        "inv_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Categorías",
        estatus="A",
    )


@inv_categorias.route("/inv_categorias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de INV CATEGORIAS inactivos"""
    return render_template(
        "inv_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Categorías inactivos",
        estatus="B",
    )


@inv_categorias.route("/inv_categorias/<int:inv_categoria_id>")
def detail(inv_categoria_id):
    """Detalle de un Categorias"""
    inv_categoria = InvCategoria.query.get_or_404(inv_categoria_id)
    return render_template("inv_categorias/detail.jinja2", inv_categoria=inv_categoria)


@inv_categorias.route("/inv_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Categoria"""
    form = InvCategoriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data)
        inv_categoria_existente = InvCategoria.query.filter_by(nombre=nombre).first()
        if inv_categoria_existente:
            flash("Ya existe una categoria con ese nombre.", "warning")
            es_valido = False
        # Si es valido insertar
        if es_valido:
            inv_categoria = InvCategoria(nombre=safe_string(form.nombre.data))
            inv_categoria.save()
            flash(f"Categorias {inv_categoria.nombre} guardado.", "success")
            return redirect(url_for("inv_categorias.list_active"))
    return render_template("inv_categorias/new.jinja2", form=form)


@inv_categorias.route("/inv_categorias/edicion/<int:inv_categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_categoria_id):
    """Editar Categoria"""
    inv_categoria = InvCategoria.query.get_or_404(inv_categoria_id)
    form = InvCategoriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data)
        inv_categoria_existente = InvCategoria.query.filter_by(nombre=nombre).first()
        if inv_categoria_existente and inv_categoria_existente.id != inv_categoria.id:
            flash("Ya existe una categoria con ese nombre.", "warning")
            es_valido = False
        # Si es valido actualizar
        if es_valido:
            inv_categoria.nombre = safe_string(form.nombre.data)
            inv_categoria.save()
            flash(f"Categorias {inv_categoria.nombre} guardado.", "success")
            return redirect(url_for("inv_categorias.detail", inv_categoria_id=inv_categoria.id))
    form.nombre.data = inv_categoria.nombre
    return render_template("inv_categorias/edit.jinja2", form=form, inv_categoria=inv_categoria)


@inv_categorias.route("/inv_categorias/eliminar/<int:inv_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_categoria_id):
    """Eliminar Categorias"""
    inv_categoria = InvCategoria.query.get_or_404(inv_categoria_id)
    if inv_categoria.estatus == "A":
        inv_categoria.delete()
        flash(f"Categorias {inv_categoria.nombre} eliminado.", "success")
    return redirect(url_for("inv_categorias.detail", inv_categoria_id=inv_categoria.id))


@inv_categorias.route("/inv_categorias/recuperar/<int:inv_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_categoria_id):
    """Recuperar Categorias"""
    inv_categoria = InvCategoria.query.get_or_404(inv_categoria_id)
    if inv_categoria.estatus == "B":
        inv_categoria.recover()
        flash(f"Categorias {inv_categoria.nombre} recuperado.", "success")
    return redirect(url_for("inv_categorias.detail", inv_categoria_id=inv_categoria.id))
