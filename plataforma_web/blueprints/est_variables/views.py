"""
Estadisticas Variables, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.est_variables.forms import EstVariableForm
from plataforma_web.blueprints.est_variables.models import EstVariable

MODULO = "ESTADISTICAS VARIABLES"

est_variables = Blueprint("est_variables", __name__, template_folder="templates")


@est_variables.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@est_variables.route("/est_variables/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Variables"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EstVariable.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(EstVariable.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("est_variables.detail", est_variable_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@est_variables.route("/est_variables")
def list_active():
    """Listado de Variables activas"""
    return render_template(
        "est_variables/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Variables de estadísticas",
        estatus="A",
    )


@est_variables.route("/est_variables/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Variables inactivas"""
    return render_template(
        "est_variables/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Variables inactivas de estadísticas",
        estatus="B",
    )


@est_variables.route("/est_variables/<int:est_variable_id>")
def detail(est_variable_id):
    """Detalle de una Variable"""
    est_variable = EstVariable.query.get_or_404(est_variable_id)
    return render_template("est_variables/detail.jinja2", est_variable=est_variable)


@est_variables.route("/est_variables/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Variable"""
    form = EstVariableForm()
    if form.validate_on_submit():
        clave = safe_clave(form.clave.data)
        descripcion = safe_string(form.descripcion.data, save_enie=True, to_uppercase=False, do_unidecode=False)
        # Validar que la clave no se repita
        if EstVariable.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
        else:
            est_variable = EstVariable(clave=clave, descripcion=descripcion)
            est_variable.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Variable {est_variable.clave}"),
                url=url_for("est_variables.detail", est_variable_id=est_variable.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("est_variables/new.jinja2", form=form)


@est_variables.route("/est_variables/edicion/<int:est_variable_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(est_variable_id):
    """Editar Variable"""
    est_variable = EstVariable.query.get_or_404(est_variable_id)
    form = EstVariableForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if est_variable.clave != clave:
            est_variable_existente = EstVariable.query.filter_by(clave=clave).first()
            if est_variable_existente and est_variable_existente.id != est_variable_id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es valido actualizar
        if es_valido:
            est_variable.clave = clave
            est_variable.descripcion = safe_string(form.descripcion.data, save_enie=True, to_uppercase=False, do_unidecode=False)
            est_variable.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editada la Variable {est_variable.clave}"),
                url=url_for("est_variables.detail", est_variable_id=est_variable.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = est_variable.clave
    form.descripcion.data = est_variable.descripcion
    return render_template("est_variables/edit.jinja2", form=form, est_variable=est_variable)


@est_variables.route("/est_variables/eliminar/<int:est_variable_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(est_variable_id):
    """Eliminar Variable"""
    est_variable = EstVariable.query.get_or_404(est_variable_id)
    if est_variable.estatus == "A":
        est_variable.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la Variable {est_variable.clave}"),
            url=url_for("est_variables.detail", est_variable_id=est_variable.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("est_variables.detail", est_variable_id=est_variable.id))


@est_variables.route("/est_variables/recuperar/<int:est_variable_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(est_variable_id):
    """Recuperar Variable"""
    est_variable = EstVariable.query.get_or_404(est_variable_id)
    if est_variable.estatus == "B":
        est_variable.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada la Variable {est_variable.clave}"),
            url=url_for("est_variables.detail", est_variable_id=est_variable.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("est_variables.detail", est_variable_id=est_variable.id))
