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
from plataforma_web.blueprints.inv_marcas.models import INVMarca

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


@inv_equipos.route("/inv_equipos/nuevo/<int:custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(custodia_id):
    """Nuevo Equipos"""
    custodia = INVCustodia.query.get_or_404(custodia_id)
    if custodia.estatus != "A":
        flash("El usuario no es activo.", "warning")
        return redirect(url_for("inv_custodia.list_active"))
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
                custodia=custodia,
                modelo=form.modelo.data,
                red=form.red.data,
                adquisicion_fecha=form.adquisicion_fecha.data,
                numero_serie=form.numero_serie.data,
                numero_inventario=form.numero_inventario.data,
                descripcion=safe_string(form.descripcion.data),
                direccion_ip=form.direccion_ip.data,
                direccion_mac=form.direccion_mac.data,
                numero_nodo=form.numero_nodo.data,
                numero_switch=form.numero_switch.data,
                numero_puerto=form.numero_puerto.data,
            )
            equipo.save()
            flash(f"Equipos {equipo.descripcion} guardado.", "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    form.custodia.data = custodia.nombre_completo
    form.email.data = custodia.usuario.email
    form.puesto.data = custodia.usuario.puesto
    form.oficina.data = str(f"{custodia.oficina.clave} - {custodia.oficina.descripcion_corta}")
    return render_template("inv_equipos/new.jinja2", form=form, custodia=custodia)


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
    if "usuario_id" in request.form:
        consulta = consulta.filter(INVCustodia.usuario_id == request.form["usuario_id"])
        # consulta = consulta.join(INVCustodia).filter(INVCustodia.usuario_id == request.form["usuario_id"])
    if "custodia_id" in request.form:
        consulta = consulta.filter_by(custodia_id=request.form["custodia_id"])
    if "modelo_equipo_id" in request.form:
        consulta = consulta.filter(INVEquipo.modelo_id == request.form["modelo_equipo_id"])
    if "modelo_id" in request.form:
        consulta = consulta.join(INVMarca).filter_by(modelo_id=request.form["modelo_id"])
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
                "adquisicion_fecha": resultado.adquisicion_fecha.strftime("%Y-%m-%d"),
                "descripcion": resultado.descripcion,
                "custodia": {
                    "nombre_completo": resultado.custodia.nombre_completo,
                    "url": url_for("inv_custodias.detail", custodia_id=resultado.custodia_id) if current_user.can_view("INV CUSTODIAS") else "",
                },
                "marca": {
                    "nombre": resultado.modelo.marca.nombre,
                    "url": url_for("inv_marcas.detail", marca_id=resultado.modelo.marca_id) if current_user.can_view("INV MARCAS") else "",
                },
                "modelo": {
                    "nombre": resultado.modelo.descripcion,
                    "url": url_for("inv_modelos.detail", modelo_id=resultado.modelo_id) if current_user.can_view("INV MODELOS") else "",
                },
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
    if form.validate_on_submit():
        equipo.modelo = form.modelo.data
        equipo.red = form.red.data
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
    form.modelo.data = equipo.modelo
    form.red.data = equipo.red
    form.adquisicion_fecha.data = equipo.adquisicion_fecha
    form.numero_serie.data = equipo.numero_serie
    form.numero_inventario.data = equipo.numero_inventario
    form.descripcion.data = safe_string(equipo.descripcion)
    form.direccion_ip.data = equipo.direccion_ip
    form.direccion_mac.data = equipo.direccion_mac
    form.numero_nodo.data = equipo.numero_nodo
    form.numero_switch.data = equipo.numero_switch
    form.numero_puerto.data = equipo.numero_puerto
    form.custodia.data = equipo.custodia.nombre_completo
    form.email.data = equipo.custodia.usuario.email
    form.puesto.data = equipo.custodia.usuario.puesto
    form.oficina.data = str(f"{equipo.custodia.oficina.clave} - {equipo.custodia.oficina.descripcion_corta}")
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
