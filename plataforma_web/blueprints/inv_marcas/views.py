"""
Inventarios Modelos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.inv_modelos.models import InvModelo

from plataforma_web.blueprints.inv_marcas.forms import InvMarcaForm, InvMarcaSearchForm

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
    if "nombre" in request.form:
        consulta = consulta.filter(InvMarca.nombre.contains(safe_string(request.form["nombre"])))
    registros = consulta.order_by(InvMarca.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_marcas.detail", marca_id=resultado.id),
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


@inv_marcas.route("/inv_marcas/<int:marca_id>")
def detail(marca_id):
    """Detalle de un Marcas"""
    marca = InvMarca.query.get_or_404(marca_id)
    modelos = InvModelo.query.filter(InvModelo.inv_marca_id == marca_id).all()
    return render_template("inv_marcas/detail.jinja2", marca=marca, modelos=modelos)


@inv_marcas.route("/inv_marcas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Marcas"""
    form = InvMarcaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la marca incorrecto. {str(err)}", "warning")
            validacion = False

        if validacion:
            marca = InvMarca(nombre=safe_string(form.nombre.data))
            marca.save()
            flash(f"Marcas {marca.nombre} guardado.", "success")
            return redirect(url_for("inv_marcas.detail", marca_id=marca.id))
    return render_template("inv_marcas/new.jinja2", form=form)


@inv_marcas.route("/inv_marcas/edicion/<int:marca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(marca_id):
    """Editar Marcas"""
    marca = InvMarca.query.get_or_404(marca_id)
    form = InvMarcaForm()
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
        nombre_existente = InvMarca.query.filter(InvMarca.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está registrado")
    return True


@inv_marcas.route("/inv_marcas/buscar", methods=["GET", "POST"])
def search():
    """Buscar Marcas"""
    form_search = InvMarcaSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data)
            if nombre != "":
                busqueda["nombre"] = nombre
                titulos.append("nombre " + nombre)
        return render_template(
            "inv_marcas/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Marcas con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("inv_marcas/search.jinja2", form=form_search)


@inv_marcas.route("/inv_marcas/eliminar/<int:marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(marca_id):
    """Eliminar Marcas"""
    marca = InvMarca.query.get_or_404(marca_id)
    if marca.estatus == "A":
        marca.delete()
        flash(f"Marcas {marca.nombre} eliminado.", "success")
    return redirect(url_for("inv_marcas.detail", marca_id=marca.id))


@inv_marcas.route("/inv_marcas/recuperar/<int:marca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(marca_id):
    """Recuperar Marcas"""
    marca = InvMarca.query.get_or_404(marca_id)
    if marca.estatus == "B":
        marca.recover()
        flash(f"Marcas {marca.nombre} recuperado.", "success")
    return redirect(url_for("inv_marcas.detail", marca_id=marca.id))
