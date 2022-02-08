"""
INVENTARIOS CUSTODIAS, vistas
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
from plataforma_web.blueprints.inv_custodias.models import INVCustodias

from plataforma_web.blueprints.inv_custodias.forms import INVCustodiasForm

MODULO = "INV CUSTODIAS"
MESES_FUTUROS = 12  # Un año a futuro, para las fechas

inv_custodias = Blueprint("inv_custodias", __name__, template_folder="templates")


@inv_custodias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_custodias.route("/inv_custodias")
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


@inv_custodias.route("/inv_custodias/<int:custodias_id>")
def detail(custodias_id):
    """Detalle de un Custodias"""
    custodia = INVCustodias.query.get_or_404(custodias_id)
    return render_template("inv_custodias/detail.jinja2", custodia=custodia)


@inv_custodias.route("/inv_custodias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Custodia"""
    form = INVCustodiasForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"La descripcion es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            custodia = INVCustodias(
                fecha=form.fecha.data,
                curp=form.curp.data,
                nombre_completo=form.nombre_completo.data,
            )
            custodia.save()
            flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", custodias_id=custodia.id))
    return render_template("inv_custodias/new.jinja2", form=form)


@inv_custodias.route("/inv_custodias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Custodias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = INVCustodias.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(INVCustodias.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "nombre_completo": {
                    "descripcion": resultado.nombre_completo,
                    "url": url_for("inv_custodias.detail", custodias_id=resultado.id),
                },
                "fecha": resultado.fecha,
                "curp": resultado.curp,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@inv_custodias.route("/inv_custodias/edicion/<int:custodias_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(custodias_id):
    """Editar Custodias"""
    custodia = INVCustodias.query.get_or_404(custodias_id)
    form = INVCustodiasForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"El custodia es incorrecto: {str(err)}", "warning")
            validacion = False

        if validacion:
            custodia.fecha = form.fecha.data
            custodia.curp = form.curp.data
            custodia.nombre_completo = form.nombre_completo.data
            custodia.save()
            flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", custodias_id=custodia.id))
    form.fecha.data = custodia.fecha
    form.curp.data = custodia.curp
    form.nombre_completo.data = custodia.nombre_completo
    return render_template("inv_custodias/edit.jinja2", form=form, custodia=custodia)


def _validar_form(fecha, form, same=False):
    if not same:
        curp_existente = INVCustodias.query.filter(INVCustodias.curp == form.curp.data).first()
        if curp_existente:
            raise Exception("La CURP ya esta en uso.")
        if fecha < date.today():
            raise Exception("La fecha no puede ser pasada.")
        fecha_futura = date.today() + relativedelta(months=+MESES_FUTUROS)
        if fecha > fecha_futura:
            raise Exception(f"La fecha no esta dentro del rango a futuro, lo máximo permitido es: {fecha_futura}")
    return True


# def _validar_fecha(fecha):
#     if fecha < date.today():
#         raise Exception("La fecha no puede ser pasada.")
#         fecha_futura = date.today() + relativedelta(months=+MESES_FUTUROS)
#         if fecha > fecha_futura:
#             raise Exception(f"La fecha no esta dentro del rango a futuro, lo máximo permitido es: {fecha_futura}")
#     return True


@inv_custodias.route("/inv_custodias/eliminar/<int:custodias_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(custodias_id):
    """Eliminar Custodias"""
    custodia = INVCustodias.query.get_or_404(custodias_id)
    if custodia.estatus == "A":
        custodia.delete()
        flash(f"Custodias {custodia.descripcion} eliminado.", "success")
    return redirect(url_for("inv_custodias.detail", custodias_id=custodia.id))


@inv_custodias.route("/inv_custodias/recuperar/<int:custodias_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(custodias_id):
    """Recuperar Custodias"""
    custodia = INVCustodias.query.get_or_404(custodias_id)
    if custodia.estatus == "B":
        custodia.recover()
        flash(f"Custodias {custodia.descripcion} recuperado.", "success")
    return redirect(url_for("inv_custodias.detail", custodias_id=custodia.id))
