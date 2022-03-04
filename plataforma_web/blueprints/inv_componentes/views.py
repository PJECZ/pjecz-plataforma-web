"""
INVENTARIOS COMPONENTES, vistas
"""
import json

from datetime import date
from dateutil.relativedelta import relativedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_componentes.models import INVComponente
from plataforma_web.blueprints.inv_componentes.forms import INVComponenteForm
from plataforma_web.blueprints.inv_equipos.models import INVEquipo

MODULO = "INV COMPONENTES"

inv_componentes = Blueprint("inv_componentes", __name__, template_folder="templates")


@inv_componentes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


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


@inv_componentes.route("/inv_componentes/<int:componente_id>")
def detail(componente_id):
    """Detalle de un Componentes"""
    componente = INVComponente.query.get_or_404(componente_id)
    return render_template("inv_componentes/detail.jinja2", componente=componente)


@inv_componentes.route("/inv_componentes/nuevo/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(equipo_id):
    """Nuevo Componentes"""
    # Validar equipo
    equipo = INVEquipo.query.get_or_404(equipo_id)
    if equipo.estatus != "A":
        flash("El equipo no es activo.", "warning")
        return redirect(url_for("inv_equipos.list_active"))
    form = INVComponenteForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"La descripcion es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            componente = INVComponente(
                categoria=form.nombre.data,
                equipo=equipo,
                descripcion=safe_string(form.descripcion.data),
                cantidad=form.cantidad.data,
                version=form.version.data,
            )
            componente.save()
            flash(f"Componentes {componente.descripcion} guardado.", "success")
            return redirect(url_for("inv_componentes.detail", componente_id=componente.id))
    return render_template("inv_componentes/new.jinja2", form=form, equipo=equipo)


@inv_componentes.route("/inv_componentes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Componentes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = INVComponente.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")

    if "descripcion" in request.form:
        consulta = consulta.orde_by(INVComponente.descripcion.like("%" + safe_string(request.form["descripcion"]) + "%"))

    registros = consulta.order_by(INVComponente.descripcion.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("inv_componentes.detail", componente_id=resultado.id),
                },
                "cantidad": resultado.cantidad,
                "version": resultado.version,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@inv_componentes.route("/inv_componentes/edicion/<int:componente_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(componente_id):
    """Editar Componentes"""
    componente = INVComponente.query.get_or_404(componente_id)
    form = INVComponenteForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"El componente es incorrecto: {str(err)}", "warning")
            validacion = False

        if validacion:
            componente.categoria = form.nombre.data
            componente.descripcion = safe_string(form.descripcion.data)
            componente.cantidad = form.cantidad.data
            componente.version = form.version.data
            componente.save()
            flash(f"Componentes {componente.descripcion} guardado.", "success")
            return redirect(url_for("inv_componentes.detail", componente_id=componente.id))
    form.nombre.data = componente.categoria
    form.descripcion.data = safe_string(componente.descripcion)
    form.cantidad.data = componente.cantidad
    form.version.data = componente.version
    return render_template("inv_componentes/edit.jinja2", form=form, componente=componente)


def _validar_form(form, same=False):
    if not same:
        descripcion_existente = INVComponente.query.filter(INVComponente.descripcion == safe_string(form.descripcion.data)).first()
        if descripcion_existente:
            raise Exception("La descripción ya está en uso.")
    return True


@inv_componentes.route("/inv_componentes/eliminar/<int:componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(componente_id):
    """Eliminar Componentes"""
    componente = INVComponente.query.get_or_404(componente_id)
    if componente.estatus == "A":
        componente.delete()
        flash(f"Componentes {componente.descripcion} eliminado.", "success")
    return redirect(url_for("inv_componentes.detail", componente_id=componente.id))


@inv_componentes.route("/inv_componentes/recuperar/<int:componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(componente_id):
    """Recuperar Componentes"""
    componente = INVComponente.query.get_or_404(componente_id)
    if componente.estatus == "B":
        componente.recover()
        flash(f"Componentes {componente.descripcion} recuperado.", "success")
    return redirect(url_for("inv_componentes.detail", componente_id=componente.id))
