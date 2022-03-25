"""
Inventarios Modelos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required


from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.usuarios.decorators import permission_required


from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_modelos.models import InvModelo
from plataforma_web.blueprints.inv_modelos.forms import InvModeloForm, InvModeloEditForm


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
    if "marca_id" in request.form:
        marca = InvMarca.query.get(request.form["marca_id"])
        if marca:
            consulta = consulta.filter(InvModelo.inv_marca == marca)
    registros = consulta.order_by(InvModelo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("inv_modelos.detail", modelo_id=resultado.id),
                },
                "marca": {"nombre": resultado.inv_marca.nombre, "url": url_for("inv_marcas.detail", marca_id=resultado.inv_marca_id)},
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


@inv_modelos.route("/inv_modelos/<int:modelo_id>")
def detail(modelo_id):
    """Detalle de un Modelos"""
    modelo = InvModelo.query.get_or_404(modelo_id)
    return render_template("inv_modelos/detail.jinja2", modelo=modelo)


@inv_modelos.route("/inv_modelos/nuevo/<int:marca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(marca_id):
    """Nuevo Modelos"""
    marca = InvMarca.query.get_or_404(marca_id)
    form = InvModeloForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Creación de la descripcion incorrecta. {str(err)}", "warning")
            validacion = False
        if validacion:
            modelo = InvModelo(
                inv_marca=marca,
                descripcion=safe_string(form.descripcion.data),
            )
            modelo.save()
            flash(f"Modelos {modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
    form.nombre.data = marca.nombre
    return render_template("inv_modelos/new.jinja2", form=form, marca=marca)


@inv_modelos.route("/inv_modelos/edicion/<int:modelo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(modelo_id):
    """Editar Modelo"""
    modelo = InvModelo.query.get_or_404(modelo_id)
    form = InvModeloEditForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            modelo.descripcion = safe_string(form.descripcion.data)
            modelo.save()
            flash(f"Modelo {modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
    form.nombre.data = modelo.inv_marca.nombre
    form.descripcion.data = modelo.descripcion
    return render_template("inv_modelos/edit.jinja2", form=form, modelo=modelo)


def _validar_form(form, same=False):
    if not same:
        descripcion_existente = InvModelo.query.filter(InvModelo.descripcion == safe_string(form.descripcion.data)).first()
        if descripcion_existente:
            raise Exception("La descripción ya está en uso. ")


@inv_modelos.route("/inv_modelos/eliminar/<int:modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(modelo_id):
    """Eliminar Modelo"""
    modelo = InvModelo.query.get_or_404(modelo_id)
    if modelo.estatus == "A":
        modelo.delete()
        flash(f"Modelo { modelo.descripcion} eliminado.", "success")
    return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))


@inv_modelos.route("/inv_modelos/recuperar/<int:modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(modelo_id):
    """Recuperar Modelo"""
    modelo = InvModelo.query.get_or_404(modelo_id)
    if modelo.estatus == "B":
        modelo.recover()
        flash(f"Modelo {modelo.descripcion} recuperado.", "success")
    return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
