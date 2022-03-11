"""
Autoridades Funcionarios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message

from plataforma_web.blueprints.autoridades_funcionarios.forms import AutoridadFuncionarioWithFuncionarioForm
from plataforma_web.blueprints.autoridades_funcionarios.models import AutoridadFuncionario
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "AUTORIDADES FUNCIONARIOS"

autoridades_funcionarios = Blueprint("autoridades_funcionarios", __name__, template_folder="templates")


@autoridades_funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades_funcionarios.route("/autoridades_funcionarios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Autoridades Funcionarios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = AutoridadFuncionario.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=request.form["autoridad_id"])
    if "funcionario_id" in request.form:
        consulta = consulta.filter_by(funcionario_id=request.form["funcionario_id"])
    registros = consulta.order_by(AutoridadFuncionario.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=resultado.id),
                },
                "autoridad": {
                    "clave": resultado.autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad_id) if current_user.can_view("AUTORIDADES") else "",
                },
                "autoridad_descripcion_corta": resultado.autoridad.descripcion_corta,
                "funcionario": {
                    "curp": resultado.funcionario.curp,
                    "url": url_for("funcionarios.detail", funcionario_id=resultado.funcionario_id) if current_user.can_view("FUNCIONARIOS") else "",
                },
                "funcionario_nombre": resultado.funcionario.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@autoridades_funcionarios.route("/autoridades_funcionarios")
def list_active():
    """Listado de Autoridades Funcionarios activos"""
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Autoridades Funcionarios",
        estatus="A",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades Funcionarios inactivos"""
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Autoridades Funcionarios inactivos",
        estatus="B",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/<int:autoridad_funcionario_id>")
def detail(autoridad_funcionario_id):
    """Detalle de un Autoridad-Funcionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    return render_template("autoridades_funcionarios/detail.jinja2", autoridad_funcionario=autoridad_funcionario)


@autoridades_funcionarios.route("/autoridades_funcionarios/nuevo_con_funcionario/<int:funcionario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_funcionario(funcionario_id):
    """Nuevo Autoridad-Funcionario con Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    form = AutoridadFuncionarioWithFuncionarioForm()
    if form.validate_on_submit():
        autoridad = form.autoridad.data
        descripcion = f"{funcionario.nombre} en {autoridad.clave}"
        if AutoridadFuncionario.query.filter(AutoridadFuncionario.autoridad == autoridad).filter(AutoridadFuncionario.funcionario == funcionario).first() is not None:
            flash(f"CONFLICTO: Ya existe {descripcion}. Si está eliminado puede recuperarlo.", "warning")
            return redirect(url_for("autoridades_funcionarios.list_inactive"))
        autoridad_funcionario = AutoridadFuncionario(
            autoridad=autoridad,
            funcionario=funcionario,
            descripcion=descripcion,
        )
        autoridad_funcionario.save()
        flash(f"Nuevo {descripcion}", "success")
        return redirect(url_for("funcionarios.detail", funcionario_id=funcionario.id))
    form.funcionario.data = funcionario.nombre
    return render_template(
        "autoridades_funcionarios/new_with_funcionario.jinja2",
        form=form,
        funcionario=funcionario,
        titulo=f"Agregar autoridad al funcionario {funcionario.nombre}",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/eliminar/<int:autoridad_funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(autoridad_funcionario_id):
    """Eliminar Autoridad-Funcionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    if autoridad_funcionario.estatus == "A":
        autoridad_funcionario.delete()
        flash(safe_message(f"Eliminado autoridad-funcionario {autoridad_funcionario.descripcion}"), "success")
        return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id))
    return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridades_funcionarios.id))


@autoridades_funcionarios.route("/autoridades_funcionarios/recuperar/<int:autoridad_funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(autoridad_funcionario_id):
    """Recuperar Autoridad-Funcionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    if autoridad_funcionario.estatus == "B":
        autoridad_funcionario.recover()
        flash(safe_message(f"Recuperado autoridad-funcionario {autoridad_funcionario.descripcion}"), "success")
        return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id))
    return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id))
