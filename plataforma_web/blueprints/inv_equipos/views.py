"""
Inventarios Equipos, vistas
"""

import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.inv_redes.models import InvRed

from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_modelos.models import InvModelo

from plataforma_web.blueprints.inv_equipos.forms import InvEquipoForm

MODULO = "INV EQUIPOS"
MESES_FUTUROS = 6  # Un año a futuro, para las fechas

inv_equipos = Blueprint("inv_equipos", __name__, template_folder="templates")


@inv_equipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_equipos.route("/inv_equipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV EQUIPOS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvEquipo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        usuario = InvCustodia.query.get(request.form["usuario_id"])
        if usuario:
            consulta = consulta.filter(InvEquipo.inv_custodia == usuario)
    if "custodia_id" in request.form:
        consulta = consulta.filter_by(inv_custodia_id=request.form["custodia_id"])
    if "modelo_id" in request.form:
        modelo = InvModelo.query.get(request.form["modelo_id"])
        if modelo:
            consulta = consulta.filter(InvEquipo.inv_modelo == modelo)
    if "red_id" in request.form:
        red = InvRed.query.get(request.form["red_id"])
        if red:
            consulta = consulta.filter(InvEquipo.inv_red == red)
    registros = consulta.order_by(InvEquipo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "equipo_id": resultado.id,
                    "url": url_for("inv_equipos.detail", equipo_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "adquisicion_fecha": resultado.adquisicion_fecha.strftime("%Y-%m-%d") if resultado.adquisicion_fecha is not None else "-",
                "usuario": {
                    "nombre_completo": resultado.inv_custodia.usuario.nombre,
                    "url": url_for("usuarios.detail", usuario_id=resultado.inv_custodia.usuario_id),
                },
                "custodia_id": {
                    "id": resultado.inv_custodia.id,
                    "url": url_for("inv_custodias.detail", custodia_id=resultado.inv_custodia.id),
                },
                "marca": {
                    "nombre": resultado.inv_modelo.inv_marca.nombre,
                    "url": url_for("inv_marcas.detail", marca_id=resultado.inv_modelo.inv_marca.id),
                },
                "modelo": {
                    "nombre": resultado.inv_modelo.descripcion,
                    "url": url_for("inv_modelos.detail", modelo_id=resultado.inv_modelo.id),
                },
                "red": {"nombre": resultado.inv_red.nombre, "url": url_for("inv_redes.detail", red_id=resultado.inv_red.id)},
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


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
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(equipo_id):
    """Detalle de un Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    return render_template("inv_equipos/detail.jinja2", equipo=equipo)


@inv_equipos.route("/inv_equipos/nuevo/<int:inv_custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(inv_custodia_id):
    """Nuevo Equipos"""
    custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if custodia.estatus != "A":
        flash("El usuario no es activo.", "warning")
        return redirect(url_for("inv_custodia.list_active"))
    form = InvEquipoForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.adquisicion_fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            equipo = InvEquipo(
                inv_custodia=custodia,
                inv_modelo=form.modelo.data,
                inv_red=form.red.data,
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
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo equipo {equipo.descripcion}"),
                url=url_for("inv_equipos.detail", equipo_id=equipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    form.custodia.data = custodia.nombre_completo
    form.email.data = custodia.usuario.email
    form.puesto.data = custodia.usuario.puesto
    form.oficina.data = str(f"{custodia.usuario.oficina.clave} - {custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_equipos/new.jinja2", form=form, custodia=custodia)


@inv_equipos.route("/inv_equipos/edicion/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(equipo_id):
    """Editar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    form = InvEquipoForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.adquisicion_fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False
        if validacion:
            equipo.inv_modelo = form.modelo.data
            equipo.inv_red = form.red.data
            equipo.adquisicion_fecha = form.adquisicion_fecha.data
            equipo.numero_serie = form.numero_serie.data
            equipo.numero_inventario = form.numero_inventario.data
            equipo.descripcion = safe_string(form.descripcion.data)
            equipo.direccion_ip = form.direccion_ip.data
            equipo.direccion_mac = form.direccion_mac.data
            equipo.numero_nodo = form.numero_nodo.data
            equipo.numero_switch = form.numero_switch.data
            equipo.numero_puerto = form.numero_puerto.data
            equipo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo equipo {equipo.descripcion}"),
                url=url_for("inv_equipos.detail", equipo_id=equipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            # flash(f"Equipos {equipo.descripcion} guardado.", "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    form.modelo.data = equipo.inv_modelo
    form.red.data = equipo.inv_red
    form.adquisicion_fecha.data = equipo.adquisicion_fecha
    form.numero_serie.data = equipo.numero_serie
    form.numero_inventario.data = equipo.numero_inventario
    form.descripcion.data = safe_string(equipo.descripcion)
    form.direccion_ip.data = equipo.direccion_ip
    form.direccion_mac.data = equipo.direccion_mac
    form.numero_nodo.data = equipo.numero_nodo
    form.numero_switch.data = equipo.numero_switch
    form.numero_puerto.data = equipo.numero_puerto
    form.custodia.data = equipo.inv_custodia.nombre_completo
    form.email.data = equipo.inv_custodia.usuario.email
    form.puesto.data = equipo.inv_custodia.usuario.puesto
    form.oficina.data = str(f"{equipo.inv_custodia.usuario.oficina.clave} - {equipo.inv_custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_equipos/edit.jinja2", form=form, equipo=equipo)


def validar_fecha(fecha):
    """Validar Fecha"""
    if fecha is not None and fecha > date.today():
        raise Exception(f"La fecha no esta dentro del rango a futuro, lo máximo permitido es: {date.today()}")
    return True


@inv_equipos.route("/inv_equipos/eliminar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(equipo_id):
    """Eliminar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "A":
        equipo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado equipo {equipo.descripcion}"),
            url=url_for("inv_equipos.detail", equipo_id=equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))


@inv_equipos.route("/inv_equipos/recuperar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(equipo_id):
    """Recuperar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "B":
        equipo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperar equipo {equipo.descripcion}"),
            url=url_for("inv_equipos.detail", equipo_id=equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
