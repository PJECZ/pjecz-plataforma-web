"""
Funcionarios Oficinas, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.funcionarios_oficinas.forms import FuncionarioOficinaForm
from plataforma_web.blueprints.funcionarios_oficinas.models import FuncionarioOficina
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios.models import Usuario

MODULO = "FUNCIONARIOS OFICINAS"

funcionarios_oficinas = Blueprint("funcionarios_oficinas", __name__, template_folder="templates")


@funcionarios_oficinas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@funcionarios_oficinas.route("/funcionarios_oficinas")
def list_active():
    """Listado de Funcionarios Oficinas activos"""
    return render_template(
        "funcionarios_oficinas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Funcionarios Oficinas",
        estatus="A",
    )


@funcionarios_oficinas.route("/funcionarios_oficinas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Funcionarios Oficinas inactivos"""
    return render_template(
        "funcionarios_oficinas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Funcionarios Oficinas inactivos",
        estatus="B",
    )


@funcionarios_oficinas.route("/funcionarios_oficinas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Funcionarios Oficinas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = FuncionarioOficina.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "funcionario_id" in request.form:
        consulta = consulta.filter_by(funcionario_id=request.form["funcionario_id"])
    if "oficina_id" in request.form:
        consulta = consulta.filter_by(oficina_id=request.form["oficina_id"])
    registros = consulta.order_by(FuncionarioOficina.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("funcionarios_oficinas.detail", funcionario_oficina_id=resultado.id),
                },
                "funcionario_nombre": resultado.funcionario.nombre,
                "oficina_clave": resultado.oficina.clave,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@funcionarios_oficinas.route("/funcionarios_oficinas/<int:funcionario_oficina_id>")
def detail(funcionario_oficina_id):
    """Detalle de un Funcionario Oficina"""
    funcionario_oficina = FuncionarioOficina.query.get_or_404(funcionario_oficina_id)
    return render_template("funcionarios_oficinas/detail.jinja2", funcionario_oficina=funcionario_oficina)


@funcionarios_oficinas.route("/funcionarios_oficinas/nuevo_con_funcionario/<int:funcionario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_funcionario(funcionario_id):
    """Nuevo Funcionario Oficina"""
    funcionario = Usuario.query.get_or_404(funcionario_id)
    form = FuncionarioOficinaForm()
    if form.validate_on_submit():
        oficina = form.oficina.data
        descripcion = f"Funcionario {funcionario.curp} en {oficina.clave}"
        funcionario_oficina = FuncionarioOficina(
            funcionario=funcionario,
            oficina=oficina,
            descripcion=descripcion,
        )
        funcionario_oficina.save()
        flash(f"Funcionario Oficina {funcionario_oficina.funcionario} guardado.", "success")
        return redirect(url_for("funcionarios_oficinas.list_active"))
    return render_template("funcionarios_oficinas/new.jinja2", form=form)


@funcionarios_oficinas.route("/funcionarios_oficinas/eliminar/<int:funcionario_oficina_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(funcionario_oficina_id):
    """Eliminar Funcionario Oficina"""
    funcionario_oficina = FuncionarioOficina.query.get_or_404(funcionario_oficina_id)
    if funcionario_oficina.estatus == "A":
        funcionario_oficina.delete()
        flash(f"Funcionario Oficina {funcionario_oficina.descripcion} eliminado.", "success")
    return redirect(url_for("funcionarios_oficinas.detail", funcionario_oficina_id=funcionario_oficina.id))


@funcionarios_oficinas.route("/funcionarios_oficinas/recuperar/<int:funcionario_oficina_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(funcionario_oficina_id):
    """Recuperar Funcionario Oficina"""
    funcionario_oficina = FuncionarioOficina.query.get_or_404(funcionario_oficina_id)
    if funcionario_oficina.estatus == "B":
        funcionario_oficina.recover()
        flash(f"Funcionario Oficina {funcionario_oficina.descripcion} recuperado.", "success")
    return redirect(url_for("funcionarios_oficinas.detail", funcionario_oficina_id=funcionario_oficina.id))
