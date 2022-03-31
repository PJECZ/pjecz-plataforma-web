"""
Inventarios Redes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required


from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_redes.models import InvRed
from plataforma_web.blueprints.inv_redes.forms import InvRedForm, InvRedSearchForm

MODULO = "INV REDES"

inv_redes = Blueprint("inv_redes", __name__, template_folder="templates")


@inv_redes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_redes.route("/inv_redes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV REDES"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvRed.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        consulta = consulta.filter(InvRed.nombre.contains(safe_string(request.form["nombre"])))
    if "tipo" in request.form:
        consulta = consulta.filter(InvRed.tipo.contains(safe_string(request.form["tipo"])))
    registros = consulta.order_by(InvRed.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_redes.detail", red_id=resultado.id),
                },
                "tipo": resultado.tipo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_redes.route("/inv_redes")
def list_active():
    """Listado de INV REDES activos"""
    return render_template(
        "inv_redes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Redes",
        estatus="A",
    )


@inv_redes.route("/inv_redes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de INV REDES inactivos"""
    return render_template(
        "inv_redes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Redes inactivos",
        estatus="B",
    )


@inv_redes.route("/inv_redes/<int:red_id>")
def detail(red_id):
    """Detalle de un Red"""
    red = InvRed.query.get_or_404(red_id)
    return render_template("inv_redes/detail.jinja2", red=red)


@inv_redes.route("/inv_redes/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Red"""
    form = InvRedForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Nombre de la red incorrecto. {str(err)}", "warning")
            validacion = False
        if validacion:
            red = InvRed(nombre=safe_string(form.nombre.data), tipo=safe_string(form.tipo.data))
            red.save()
            flash(f"Red {red.nombre} guardado.", "success")
            return redirect(url_for("inv_redes.detail", red_id=red.id))
    return render_template("inv_redes/new.jinja2", form=form)


@inv_redes.route("/inv_redes/edicion/<int:red_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(red_id):
    """Editar Red"""
    red = InvRed.query.get_or_404(red_id)
    form = InvRedForm()
    if form.validate_on_submit():
        red.nombre = safe_string(form.nombre.data)
        red.tipo = form.tipo.data
        red.save()
        flash(f"Red {red.nombre} guardado.", "success")
        return redirect(url_for("inv_redes.detail", red_id=red.id))
    form.nombre.data = red.nombre
    form.tipo.data = red.tipo
    return render_template("inv_redes/edit.jinja2", form=form, red=red)


def _validar_form(form, same=False):
    if not same:
        nombre_existente = InvRed.query.filter(InvRed.nombre == safe_string(form.nombre.data)).first()
        if nombre_existente:
            raise Exception("El nombre ya está registrado, verifique en el listado de inactivos")
    return True


@inv_redes.route("/inv_redes/buscar", methods=["GET", "POST"])
def search():
    """Buscar redes"""
    form_search = InvRedSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data)
            if nombre != "":
                busqueda["nombre"] = nombre
                titulos.append("nombre " + nombre)
        if form_search.tipo.data:
            tipo = safe_string(form_search.tipo.data)
            if tipo != "":
                busqueda["tipo"] = tipo
                titulos.append("tipo " + tipo)
        return render_template(
            "inv_redes/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="redes con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("inv_redes/search.jinja2", form=form_search)


@inv_redes.route("/inv_redes/eliminar/<int:red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(red_id):
    """Eliminar Red"""
    red = InvRed.query.get_or_404(red_id)
    if red.estatus == "A":
        red.delete()
        flash(f"Red {red.nombre} eliminado.", "success")
    return redirect(url_for("inv_redes.detail", red_id=red.id))


@inv_redes.route("/inv_redes/recuperar/<int:red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(red_id):
    """Recuperar Red"""
    red = InvRed.query.get_or_404(red_id)
    if red.estatus == "B":
        red.recover()
        flash(f"Red {red.nombre} recuperado.", "success")
    return redirect(url_for("inv_redes.detail", red_id=red.id))
