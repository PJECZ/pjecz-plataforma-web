"""
Inventarios Categorías, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_categorias.models import InvCategoria

from plataforma_web.blueprints.inv_categorias.forms import InvCategoriaForm

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
    registros = consulta.order_by(InvCategoria.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_categorias.detail", categoria_id=resultado.id),
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
        titulo="INV CATEGORIAS inactivos",
        estatus="B",
    )


@inv_categorias.route("/inv_categorias/<int:categoria_id>")
def detail(categoria_id):
    """Detalle de un Categorias"""
    categoria = InvCategoria.query.get_or_404(categoria_id)
    return render_template("inv_categorias/detail.jinja2", categoria=categoria)


@inv_categorias.route("/inv_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Categoria"""
    form = InvCategoriaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la categoria incorrecto. {str(err)}", "warning")
            validacion = False

        if validacion:
            categoria = InvCategoria(nombre=safe_string(form.nombre.data))
            categoria.save()
            flash(f"Categorias {categoria.nombre} guardado.", "success")
            return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))
    return render_template("inv_categorias/new.jinja2", form=form)


@inv_categorias.route("/inv_categorias/edicion/<int:categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(categoria_id):
    """Editar Categoria"""
    categoria = InvCategoria.query.get_or_404(categoria_id)
    form = InvCategoriaForm()
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
        nombre_existente = InvCategoria.query.filter(InvCategoria.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está registrado.")
    return True


@inv_categorias.route("/inv_categorias/eliminar/<int:categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(categoria_id):
    """Eliminar Categorias"""
    categoria = InvCategoria.query.get_or_404(categoria_id)
    if categoria.estatus == "A":
        categoria.delete()
        flash(f"Categorias {categoria.nombre} eliminado.", "success")
    return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))


@inv_categorias.route("/inv_categorias/recuperar/<int:categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(categoria_id):
    """Recuperar Categorias"""
    categoria = InvCategoria.query.get_or_404(categoria_id)
    if categoria.estatus == "B":
        categoria.recover()
        flash(f"Categorias {categoria.nombre} recuperado.", "success")
    return redirect(url_for("inv_categorias.detail", categoria_id=categoria.id))
