"""
INVENTARIOS CUSTODIAS, vistas
"""
import json

from datetime import date
from dateutil.relativedelta import relativedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.inv_equipos.models import INVEquipo
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_custodias.models import INVCustodia
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.inv_custodias.forms import INVCustodiaForm

MODULO = "INV CUSTODIAS"
MESES_FUTUROS = 6  # Un año a futuro, para las fechas

inv_custodias = Blueprint("inv_custodias", __name__, template_folder="templates")


@inv_custodias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_custodias.route("/inv_custodias/")
def list_active():
    """Listado de Custodias activos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Custodias",
        estatus="A",
    )


@inv_custodias.route("/inv_custodias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Custodias inactivos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Custodias inactivos",
        estatus="B",
    )


@inv_custodias.route("/inv_custodias/<int:custodia_id>")
def detail(custodia_id):
    """Detalle de un Custodias"""
    custodia = INVCustodia.query.get_or_404(custodia_id)
    return render_template("inv_custodias/detail.jinja2", custodia=custodia)


@inv_custodias.route("/inv_custodias/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(usuario_id):
    """Nuevo Custodias"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = INVCustodiaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False
        if validacion:
            custodia = INVCustodia(fecha=form.fecha.data, usuario=usuario, nombre_completo=usuario.nombre, curp=usuario.curp, oficina=usuario.oficina)
            custodia.save()
            flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))
    form.usuario.data = str(f"{usuario.nombre}")
    form.oficina.data = str(f"{usuario.oficina.clave} - {usuario.oficina.descripcion_corta}")
    return render_template("inv_custodias/new.jinja2", form=form, usuario=usuario)


@inv_custodias.route("/inv_custodias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Custodias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = INVCustodia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])

    registros = consulta.order_by(INVCustodia.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "custodia_id": resultado.id,
                    "url": url_for("inv_custodias.detail", custodia_id=resultado.id),
                },
                "nombre_completo": resultado.nombre_completo,
                "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                "oficina": {
                    "clave": resultado.usuario.oficina.clave,
                    "url": url_for("oficinas.detail", oficina_id=resultado.oficina_id) if current_user.can_view("OFICINAS") else "",
                },
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@inv_custodias.route("/inv_custodias/edicion/<int:custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(custodia_id):
    """Editar Custodias"""
    custodia = INVCustodia.query.get_or_404(custodia_id)
    form = INVCustodiaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False
        if validacion:
            custodia.fecha = form.fecha.data
            custodia.save()
            flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))
    form.fecha.data = custodia.fecha
    form.usuario.data = custodia.usuario.nombre
    form.oficina.data = str(f"{custodia.oficina.clave} - {custodia.oficina.descripcion_corta}")
    return render_template("inv_custodias/edit.jinja2", form=form, custodia=custodia)


def validar_fecha(fecha):
    """Validar Fecha"""
    if fecha is not None and fecha > date.today():
        raise Exception(f"La fecha no esta dentro del rango a futuro, lo máximo permitido es: {date.today()}")
    return True


@inv_custodias.route("/inv_custodias/eliminar/<int:custodia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(custodia_id):
    """Eliminar Custodias"""
    custodia = INVCustodia.query.get_or_404(custodia_id)
    if custodia.estatus == "A":
        custodia.delete()
        flash(f"Custodias {custodia.nombre_completo} eliminado.", "success")
    return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))


@inv_custodias.route("/inv_custodias/recuperar/<int:custodia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(custodia_id):
    """Recuperar Custodias"""
    custodia = INVCustodia.query.get_or_404(custodia_id)
    if custodia.estatus == "B":
        custodia.recover()
        flash(f"Custodias {custodia.nombre_completo} recuperado.", "success")
    return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))
