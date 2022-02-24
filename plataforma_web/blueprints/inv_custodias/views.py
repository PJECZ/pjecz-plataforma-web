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
MESES_FUTUROS = 12  # Un año a futuro, para las fechas

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
    # equipos = INVEquipo.query.filter(INVEquipo.custodia_id == custodia_id).all()
    return render_template("inv_custodias/detail.jinja2", custodia=custodia)


@inv_custodias.route("/inv_custodias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Custodias"""
    oficina = Oficina.query.join(Usuario).filter(Usuario.id == current_user.id).first()
    form = INVCustodiaForm()
    if form.validate_on_submit():
        custodia = INVCustodia(
            fecha=form.fecha.data,
            usuario=current_user,
            nombre_completo=current_user.nombre,
            curp=current_user.curp,
            oficina=oficina,
        )
        custodia.save()
        flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
        return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))
    form.usuario.data = str(current_user.nombre)
    form.oficina.data = str(f"{oficina.clave} - {oficina.descripcion_corta}")
    return render_template("inv_custodias/new.jinja2", form=form)


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

    registros = consulta.order_by(INVCustodia.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "nombre_completo": {
                    "descripcion": resultado.nombre_completo,
                    "url": url_for("inv_custodias.detail", custodia_id=resultado.id),
                },
                "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                "curp": resultado.curp,
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
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False

        if validacion:
            custodia.fecha = form.fecha.data
            custodia.curp = current_user.curp
            custodia.nombre_completo = current_user.nombre
            custodia.usuario = current_user
            custodia.save()
            flash(f"Custodias {custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", custodia_id=custodia.id))
    form.fecha.data = custodia.fecha
    form.usuario.data = str(current_user.nombre)
    return render_template("inv_custodias/edit.jinja2", form=form, custodia=custodia)


def _validar_form(form, same=False):
    if not same:
        curp_existente = INVCustodia.query.filter(INVCustodia.curp == form.curp.data).first()
        if curp_existente:
            raise Exception("La CURP ya esta en uso.")
        nombre_existente = INVCustodia.query.filter(INVCustodia.nombre_completo == form.nombre_completo.data).first()
        if nombre_existente:
            raise Exception("El nombre ya esta en uso.")
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
