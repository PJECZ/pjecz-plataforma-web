"""
Inventarios Componentes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.inv_categorias.models import InvCategoria
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_componentes.models import InvComponente
from plataforma_web.blueprints.inv_componentes.forms import InvComponenteForm
from plataforma_web.blueprints.inv_equipos.models import InvEquipo

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
    if "equipo_id" in request.form:
        consulta = consulta.filter_by(inv_equipo_id=request.form["equipo_id"])
    if "categoria_id" in request.form:
        categoria = InvCategoria.query.get(request.form["categoria_id"])
        if categoria:
            consulta = consulta.filter(InvComponente.categoria == categoria)
    registros = consulta.order_by(InvComponente.id).offset(start).limit(rows_per_page).all()
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
                "categoria": {
                    "nombre": resultado.categoria.nombre,
                    "url": url_for("inv_categorias.detail", categoria_id=resultado.categoria.id),
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


@inv_componentes.route("/inv_componentes/<int:componente_id>")
def detail(componente_id):
    """Detalle de un Componentes"""
    componente = InvComponente.query.get_or_404(componente_id)
    return render_template("inv_componentes/detail.jinja2", componente=componente)


@inv_componentes.route("/inv_componentes/nuevo/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(equipo_id):
    """Nuevo Componentes"""
    # Validar equipo
    equipo = InvEquipo.query.get_or_404(equipo_id)
    if equipo.estatus != "A":
        flash("El equipo no es activo.", "warning")
        return redirect(url_for("inv_equipos.list_active"))
    form = InvComponenteForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, equipo_id)
            validacion = True
        except Exception as err:
            flash(f"La descripcion es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            componente = InvComponente(
                categoria=form.nombre.data,
                equipo=equipo,
                descripcion=safe_string(form.descripcion.data),
                cantidad=form.cantidad.data,
                version=form.version.data,
            )
            componente.save()
            flash(f"Componentes {componente.descripcion} guardado.", "success")
            return redirect(url_for("inv_componentes.detail", componente_id=componente.id))
    form.equipo.data = equipo.id
    form.marca.data = equipo.modelo.marca.nombre
    form.descripcion_equipo.data = equipo.descripcion
    form.usuario.data = equipo.custodia.nombre_completo
    form.descripcion.data = form.nombre.data
    return render_template("inv_componentes/new.jinja2", form=form, equipo=equipo)


@inv_componentes.route("/inv_componentes/edicion/<int:componente_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(componente_id):
    """Editar Componentes"""
    componente = InvComponente.query.get_or_404(componente_id)
    form = InvComponenteForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, componente.inv_equipo_id, True)
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
    form.equipo.data = componente.equipo.id
    form.marca.data = componente.equipo.modelo.marca.nombre
    form.descripcion_equipo.data = componente.equipo.descripcion
    form.usuario.data = componente.equipo.custodia.nombre_completo
    return render_template("inv_componentes/edit.jinja2", form=form, componente=componente)


def _validar_form(form, inv_equipo_id, same=False):
    if not same:
        descripcion_existente = InvComponente.query.filter(InvComponente.descripcion == safe_string(form.descripcion.data)).filter(InvComponente.inv_equipo_id == inv_equipo_id).first()
        if descripcion_existente:
            raise Exception("La descripción ya está en uso.")
    return True


@inv_componentes.route("/inv_componentes/eliminar/<int:componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(componente_id):
    """Eliminar Componentes"""
    componente = InvComponente.query.get_or_404(componente_id)
    if componente.estatus == "A":
        componente.delete()
        flash(f"Componentes {componente.descripcion} eliminado.", "success")
    return redirect(url_for("inv_componentes.detail", componente_id=componente.id))


@inv_componentes.route("/inv_componentes/recuperar/<int:componente_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(componente_id):
    """Recuperar Componentes"""
    componente = InvComponente.query.get_or_404(componente_id)
    if componente.estatus == "B":
        componente.recover()
        flash(f"Componentes {componente.descripcion} recuperado.", "success")
    return redirect(url_for("inv_componentes.detail", componente_id=componente.id))
