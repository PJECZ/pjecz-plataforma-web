"""
INVENTARIOS EQUIPOS, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_equipos.models import INVEquipos

from plataforma_web.blueprints.inv_equipos.forms import InvEquiposForm

MODULO = "INV EQUIPOS"

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


@inv_equipos.route("/inv_equipos/<int:inv_equipos_id>")
def detail(inv_equipos_id):
    """Detalle de un Equipos"""
    equipos = INVEquipos.query.get_or_404(inv_equipos_id)
    return render_template("inv_equipos/detail.jinja2", equipos=equipos)


@inv_equipos.route("/inv_equipos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Equipos"""
    form = InvEquiposForm()
    if form.validate_on_submit():
        equipos = INVEquipos(
            adquisicion_fecha=form.adquisicion_fecha.data,
            numero_serie=form.numero_serie.data,
            numero_inventario=form.numero_inventario.data,
            descripcion=form.descripcion.data,
            direccion_ip=form.direccion_ip.data,
            direccion_mac=form.direccion_mac.data,
            numero_nodo=form.numero_nodo.data,
            numero_switch=form.numero_switch.data,
            numero_puerto=form.numero_puerto.data,
        )
        equipos.save()
        flash(f"Equipos {equipos.equipos} guardado.", "success")
        return redirect(url_for("inv_equipos.detail", equipo_id=equipos.id))
    return render_template("inv_equipos/new.jinja2", form=form)
