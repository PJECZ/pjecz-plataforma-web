"""
Centrso de Trabajo, vistas
"""
import json
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.centros_trabajos.forms import CentroTrabajoForm, CentroTrabajoSearchForm
from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "CENTROS TRABAJOS"

centros_trabajos = Blueprint("centros_trabajos", __name__, template_folder="templates")


@centros_trabajos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@centros_trabajos.route("/centros_trabajos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Centros de Trabajos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CentroTrabajo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "clave" in request.form:
        consulta = consulta.filter(CentroTrabajo.clave.contains(safe_clave(request.form["clave"])))
    if "nombre" in request.form:
        consulta = consulta.filter(CentroTrabajo.nombre.contains(safe_string(request.form["nombre"])))
    registros = consulta.order_by(CentroTrabajo.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("centros_trabajos.detail", centro_trabajo_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "telefono": resultado.telefono,
                "distrito": {
                    "nombre_corto": resultado.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@centros_trabajos.route("/centros_trabajos")
def list_active():
    """Listado de Centros de Trabajo activos"""
    return render_template(
        "centros_trabajos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Centros de Trabajo",
        estatus="A",
        form=CentroTrabajoSearchForm(),
    )


@centros_trabajos.route("/centros_trabajos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Centros de Trabajo inactivos"""
    return render_template(
        "centros_trabajos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Centros de Trabajo inactivos",
        estatus="B",
        form=CentroTrabajoSearchForm(),
    )


@centros_trabajos.route("/centros_trabajos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Centros de Trabajo"""
    form_search = CentroTrabajoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.clave.data:
            clave = safe_clave(form_search.clave.data)
            if clave != "":
                busqueda["clave"] = clave
                titulos.append("clave " + clave)
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data, save_enie=True)
            if nombre != "":
                busqueda["nombre"] = nombre
                titulos.append("nombre " + nombre)
        return render_template(
            "centros_trabajos/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Centros de Trabajo con " + ", ".join(titulos),
            estatus="A",
            form=form_search,
        )
    return render_template("centros_trabajos/search.jinja2", form=form_search)


@centros_trabajos.route("/centros_trabajos/<int:centro_trabajo_id>")
def detail(centro_trabajo_id):
    """Detalle de un Centro de Trabajo"""
    centro_trabajo = CentroTrabajo.query.get_or_404(centro_trabajo_id)
    return render_template("centros_trabajos/detail.jinja2", centro_trabajo=centro_trabajo)


@centros_trabajos.route("/centros_trabajos/edicion/<int:centro_trabajo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(centro_trabajo_id):
    """Editar Centro de Trabajo"""
    centro_trabajo = CentroTrabajo.query.get_or_404(centro_trabajo_id)
    form = CentroTrabajoForm()
    if form.validate_on_submit():
        centro_trabajo.nombre = safe_string(form.nombre.data, save_enie=True)
        centro_trabajo.telefono = safe_string(form.telefono.data)
        centro_trabajo.distrito = form.distrito.data
        centro_trabajo.domicilio = form.domicilio.data
        centro_trabajo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Centro de Trabajo {centro_trabajo.nombre}"),
            url=url_for("centros_trabajos.detail", centro_trabajo_id=centro_trabajo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.clave.data = centro_trabajo.clave  # Read only
    form.nombre.data = centro_trabajo.nombre
    form.telefono.data = centro_trabajo.telefono
    form.distrito.data = centro_trabajo.distrito
    form.domicilio.data = centro_trabajo.domicilio
    return render_template("centros_trabajos/edit.jinja2", form=form, centro_trabajo=centro_trabajo)
