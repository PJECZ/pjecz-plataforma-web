"""
Inventarios Redes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_redes.forms import InvRedForm
from plataforma_web.blueprints.inv_redes.models import InvRed
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV REDES"

inv_redes = Blueprint("inv_redes", __name__, template_folder="templates")


@inv_redes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_redes.route("/inv_redes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Redes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvRed.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(InvRed.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("inv_redes.detail", inv_red_id=resultado.id),
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


@inv_redes.route("/inv_redes/<int:inv_red_id>")
def detail(inv_red_id):
    """Detalle de un Red"""
    inv_red = InvRed.query.get_or_404(inv_red_id)
    return render_template("inv_redes/detail.jinja2", inv_red=inv_red)


@inv_redes.route("/inv_redes/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Red"""
    form = InvRedForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data, save_enie=True)
        inv_red_existente = InvRed.query.filter_by(nombre=nombre).first()
        if inv_red_existente:
            flash("Ya existe una red con ese nombre.", "warning")
            es_valido = False
        # Si es valido insertar
        if es_valido:
            red = InvRed(nombre=nombre, tipo=safe_string(form.tipo.data))
            red.save()
            flash(f"Red {red.nombre} guardado.", "success")
            return redirect(url_for("inv_redes.list_active"))
    return render_template("inv_redes/new.jinja2", form=form)


@inv_redes.route("/inv_redes/edicion/<int:inv_red_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_red_id):
    """Editar Red"""
    inv_red = InvRed.query.get_or_404(inv_red_id)
    form = InvRedForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que no exista ese nombre
        nombre = safe_string(form.nombre.data, save_enie=True)
        inv_red_existente = InvRed.query.filter_by(nombre=nombre).first()
        if inv_red_existente and inv_red_existente.id != inv_red.id:
            flash("Ya existe una red con ese nombre.", "warning")
            es_valido = False
        # Si es valido actualizar
        if es_valido:
            inv_red.nombre = nombre
            inv_red.tipo = form.tipo.data
            inv_red.save()
            flash(f"Red {inv_red.nombre} guardado.", "success")
            return redirect(url_for("inv_redes.detail", inv_red_id=inv_red.id))
    form.nombre.data = inv_red.nombre
    form.tipo.data = inv_red.tipo
    return render_template("inv_redes/edit.jinja2", form=form, inv_red=inv_red)


@inv_redes.route("/inv_redes/eliminar/<int:inv_red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_red_id):
    """Eliminar Red"""
    inv_red = InvRed.query.get_or_404(inv_red_id)
    if inv_red.estatus == "A":
        inv_red.delete()
        flash(f"Red {inv_red.nombre} eliminado.", "success")
    return redirect(url_for("inv_redes.detail", inv_red_id=inv_red.id))


@inv_redes.route("/inv_redes/recuperar/<int:inv_red_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_red_id):
    """Recuperar Red"""
    inv_red = InvRed.query.get_or_404(inv_red_id)
    if inv_red.estatus == "B":
        inv_red.recover()
        flash(f"Red {inv_red.nombre} recuperado.", "success")
    return redirect(url_for("inv_redes.detail", inv_red_id=inv_red.id))
