"""
INVENTARIOS EQUIPOS, vistas
"""

from datetime import date
from dateutil.relativedelta import relativedelta

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_equipos.models import INVEquipo
from plataforma_web.blueprints.inv_componentes.models import INVComponente
from plataforma_web.blueprints.inv_equipos_fotos.models import INVEquipoFoto
from plataforma_web.blueprints.inv_custodias.models import INVCustodia

from plataforma_web.blueprints.inv_equipos.forms import INVEquipoForm

MODULO = "INV EQUIPOS"
MESES_FUTUROS = 12  # Un año a futuro, para las fechas

inv_equipos = Blueprint("inv_equipos", __name__, template_folder="templates")


@inv_equipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_equipos.route("/inv_equipos")
def list_active():
    """Listado de Equipos activos"""
    return render_template(
        "inv_equipos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Equipos",
        estatus="A",
    )


@inv_equipos.route("/inv_equipos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Equipos inactivos"""
    return render_template(
        "inv_equipos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Equipos inactivos",
        estatus="B",
    )


@inv_equipos.route("/inv_equipos/<int:equipo_id>")
def detail(equipo_id):
    """Detalle de un Equipos"""
    equipo = INVEquipo.query.get_or_404(equipo_id)
    componentes = INVComponente.query.filter(INVComponente.equipo_id == equipo_id).all()
    fotos = INVEquipoFoto.query.filter(INVEquipoFoto.equipo_id == equipo_id).all()
    return render_template("inv_equipos/detail.jinja2", equipo=equipo, componentes=componentes, fotos=fotos)


@inv_equipos.route("/inv_equipos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Equipos"""
    form = INVEquipoForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.adquisicion_fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            equipo = INVEquipo(
                modelo=form.modelo.data,
                red=form.nombre_red.data,
                adquisicion_fecha=form.adquisicion_fecha.data,
                numero_serie=form.numero_serie.data,
                numero_inventario=form.numero_inventario.data,
                descripcion=safe_string(form.descripcion.data),
                direccion_ip=form.direccion_ip.data,
                direccion_mac=form.direccion_mac.data,
                numero_nodo=form.numero_nodo.data,
                numero_switch=form.numero_switch.data,
                numero_puerto=form.numero_puerto.data,
                custodia=current_user,
            )
            equipo.save()
            flash(f"Equipos {equipo.descripcion} guardado.", "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    return render_template("inv_equipos/new.jinja2", form=form)


@inv_equipos.route("/inv_equipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Equipos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = INVEquipo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(INVEquipo.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "numero_inventario": {
                    "descripcion": resultado.numero_inventario,
                    "url": url_for("inv_equipos.detail", equipo_id=resultado.id),
                },
                "numero_serie": resultado.numero_serie,
                "adquisicion_fecha": resultado.adquisicion_fecha.strftime("%Y-%m-%d 00:00:00"),
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@inv_equipos.route("/inv_equipos/edicion/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(equipo_id):
    """Editar Equipos"""
    equipo = INVEquipo.query.get_or_404(equipo_id)
    form = INVEquipoForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.adquisicion_fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            equipo.adquisicion_fecha = form.adquisicion_fecha.data
            equipo.numero_serie = form.numero_serie.data
            equipo.numero_invenatario = form.numero_inventario.data
            equipo.descripcion = safe_string(form.descripcion.data)
            equipo.direccion_ip = form.direccion_ip.data
            equipo.direccion_mac = form.direccion_mac.data
            equipo.numero_nodo = form.numero_nodo.data
            equipo.numero_switch = form.numero_switch.data
            equipo.numero_puerto = form.numero_puerto.data
            equipo.save()
            flash(f"Equipos {equipo.descripcion} guardado.", "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    form.adquisicion_fecha.data = equipo.adquisicion_fecha
    form.numero_serie.data = equipo.numero_serie
    form.numero_inventario.data = equipo.numero_inventario
    form.descripcion.data = safe_string(equipo.descripcion)
    form.direccion_ip.data = equipo.direccion_ip
    form.direccion_mac.data = equipo.direccion_mac
    form.numero_nodo.data = equipo.numero_nodo
    form.numero_switch.data = equipo.numero_switch
    form.numero_puerto.data = equipo.numero_puerto
    return render_template("inv_equipos/edit.jinja2", form=form, equipo=equipo)


def validar_fecha(fecha):
    """Validar Fecha"""
    if fecha < date.today():
        raise Exception("La fecha no puede ser pasada.")
    fecha_futura = date.today() + relativedelta(months=+MESES_FUTUROS)
    if fecha > fecha_futura:
        raise Exception(f"La fecha no esta dentro del rango a futuro, lo máximo permitido es: {fecha_futura}")
    return True


@inv_equipos.route("/inv_equipos/eliminar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(equipo_id):
    """Eliminar Equipos"""
    equipo = INVEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "A":
        equipo.delete()
        flash(f"Equipos {equipo.numero_inventario} eliminado.", "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))


@inv_equipos.route("/inv_equipos/recuperar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(equipo_id):
    """Recuperar Equipos"""
    equipo = INVEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "B":
        equipo.recover()
        flash(f"Equipos {equipo.numero_inventario} recuperado.", "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
