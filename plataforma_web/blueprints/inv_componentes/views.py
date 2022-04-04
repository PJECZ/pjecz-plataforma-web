"""
Inventarios Componentes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_componentes.models import InvComponente
from plataforma_web.blueprints.inv_componentes.forms import InvComponenteForm, InvComponenteEditForm
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV COMPONENTES"

inv_componentes = Blueprint("inv_componentes", __name__, template_folder="templates")


@inv_componentes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_componentes.route("/inv_componentes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV COMPONENTES"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvComponente.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "inv_equipo_id" in request.form:
        consulta = consulta.filter_by(inv_equipo_id=request.form["inv_equipo_id"])
    if "inv_categoria_id" in request.form:
        consulta = consulta.filter_by(inv_categoria_id=request.form["inv_categoria_id"])
    registros = consulta.order_by(InvComponente.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("inv_componentes.detail", inv_componente_id=resultado.id),
                },
                "inv_categoria": {
                    "nombre": resultado.inv_categoria.nombre,
                    "url": url_for("inv_categorias.detail", inv_categoria_id=resultado.inv_categoria_id) if current_user.can_view("INV CATEGORIAS") else "",
                },
                "cantidad": resultado.cantidad,
                "version": resultado.version,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_componentes.route("/inv_componentes")
def list_active():
    """Listado de Componentes activos"""
    return render_template(
        "inv_componentes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Componentes",
        estatus="A",
    )


@inv_componentes.route("/inv_componentes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Componentes inactivos"""
    return render_template(
        "inv_componentes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Componentes inactivos",
        estatus="B",
    )


@inv_componentes.route("/inv_componentes/<int:inv_componente_id>")
def detail(inv_componente_id):
    """Detalle de un Componentes"""
    inv_componente = InvComponente.query.get_or_404(inv_componente_id)
    return render_template("inv_componentes/detail.jinja2", inv_componente=inv_componente)


@inv_componentes.route("/inv_componentes/nuevo/<int:inv_equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(inv_equipo_id):
    """Nuevo Componentes"""
    # Validar equipo
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    if inv_equipo.estatus != "A":
        flash("El equipo no es activo.", "warning")
        return redirect(url_for("inv_equipos.list_active"))
    form = InvComponenteForm()
    if form.validate_on_submit():
        inv_componente = InvComponente(
            inv_categoria=form.nombre.data,
            inv_equipo=inv_equipo,
            descripcion=safe_string(form.descripcion.data),
            cantidad=form.cantidad.data,
            version=form.version.data,
        )
        inv_componente.save()
        flash(f"Componentes {inv_componente.descripcion} guardado.", "success")
        return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))
    form.inv_equipo.data = inv_equipo.id
    form.inv_marca.data = inv_equipo.inv_modelo.inv_marca.nombre  # Read only
    form.descripcion_equipo.data = inv_equipo.descripcion  # Read only
    form.usuario.data = inv_equipo.inv_custodia.nombre_completo  # Read only
    return render_template("inv_componentes/new.jinja2", form=form, inv_equipo=inv_equipo)


@inv_componentes.route("/inv_componentes/edicion/<int:inv_componente_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_componente_id):
    """Editar Componentes"""
    inv_componente = InvComponente.query.get_or_404(inv_componente_id)
    form = InvComponenteEditForm()
    if form.validate_on_submit():
        inv_componente.categoria = form.nombre.data
        inv_componente.descripcion = safe_string(form.descripcion.data)
        inv_componente.cantidad = form.cantidad.data
        inv_componente.version = form.version.data
        inv_componente.save()
        flash(f"Componentes {inv_componente.descripcion} guardado.", "success")
        return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))
    form.nombre.data = inv_componente.inv_categoria.nombre
    form.descripcion.data = safe_string(inv_componente.descripcion)
    form.cantidad.data = inv_componente.cantidad
    form.version.data = inv_componente.version
    form.inv_equipo.data = inv_componente.inv_equipo.id
    form.inv_marca.data = inv_componente.inv_equipo.inv_modelo.inv_marca.nombre
    form.descripcion_equipo.data = inv_componente.inv_equipo.descripcion
    form.usuario.data = inv_componente.inv_equipo.inv_custodia.nombre_completo
    return render_template("inv_componentes/edit.jinja2", form=form, inv_componente=inv_componente)


@inv_componentes.route("/inv_componentes/eliminar/<int:inv_componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_componente_id):
    """Eliminar Componentes"""
    inv_componente = InvComponente.query.get_or_404(inv_componente_id)
    if inv_componente.estatus == "A":
        inv_componente.delete()
        flash(safe_message(f"Eliminar componente {inv_componente.descripcion}"), "success")
        return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))
    return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))


@inv_componentes.route("/inv_componentes/recuperar/<int:inv_componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_componente_id):
    """Recuperar Componentes"""
    inv_componente = InvComponente.query.get_or_404(inv_componente_id)
    if inv_componente.estatus == "B":
        inv_componente.recover()
        flash(safe_message(f"Recuperado componente {inv_componente.descripcion}"), "success")
        return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))
    return redirect(url_for("inv_componentes.detail", inv_componente_id=inv_componente.id))
