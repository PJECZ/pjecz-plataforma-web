"""
Tesis Jusridprudencias Funcionarios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia
from plataforma_web.blueprints.tesis_jurisprudencias_funcionarios.models import TesisJurisprudenciaFuncionario
from plataforma_web.blueprints.tesis_jurisprudencias_funcionarios.forms import TesisFuncionarioWithTesisForm

MODULO = "TESIS JURISPRUDENCIAS"

tesis_jurisprudencias_funcionarios = Blueprint("tesis_jurisprudencias_funcionarios", __name__, template_folder="templates")


@tesis_jurisprudencias_funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios")
def list_active():
    """Listado de Funcionarios que tienen una Tesis y Jurisprudencia activos"""
    tesis_jurisprudencias_funcionarios_activos = TesisJurisprudenciaFuncionario.query.filter(TesisJurisprudenciaFuncionario.estatus == "A").all()
    return render_template(
        "tesis_jurisprudencias_funcionarios/list.jinja2",
        tesis_jurisprudencias_funcionarios=tesis_jurisprudencias_funcionarios_activos,
        titulo="Funcionarios que tienen una Tesis y Jurisprudencia ",
        estatus="A",
    )


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios/<int:tesis_jurisprudencia_funcionario_id>")
def detail(tesis_jurisprudencia_funcionario_id):
    """Detalle de una Tesis-Jurisprudencia Funcionario"""
    tesis_jurisprudencia_funcionario = TesisJurisprudenciaFuncionario.query.get_or_404(tesis_jurisprudencia_funcionario_id)
    return render_template("tesis_jurisprudencias_funcionarios/detail.jinja2", tesis_jurisprudencia_funcionario=tesis_jurisprudencia_funcionario)


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios/nuevo_con_tesis/<int:tesis_jurisprudencias_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_tesis(tesis_jurisprudencias_id):
    """Nuevo Tesis-Funcionario con Tesis"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencias_id)
    form = TesisFuncionarioWithTesisForm()
    if form.validate_on_submit():
        funcionario = form.funcionario.data
        descripcion = f"{funcionario.nombres} en {tesis_jurisprudencia.clave_control} "
        if TesisJurisprudenciaFuncionario.query.filter(TesisJurisprudenciaFuncionario.tesis_jurisprudencias_id == tesis_jurisprudencias_id).filter(TesisJurisprudenciaFuncionario.funcionario_id == funcionario.id).first() is not None:
            flash(f"CONFLICTO: Ya existe el funcionario {descripcion}. Mejor recupere el registro.", "warning")
            return redirect(url_for("tesis_jurisprudencias_funcionarios.list_inactive", tesis_jurisprudencias_id=tesis_jurisprudencias_id))
        tesis_funcionario = TesisJurisprudenciaFuncionario(
            funcionario=funcionario,
            tesis_jurisprudencias=tesis_jurisprudencia,
        )
        tesis_funcionario.save()
        flash(safe_message(f"{descripcion} guardado"), "success")
        return redirect(
            url_for("tesis_jurisprudencias_funcionarios.detail", tesis_jurisprudencia_funcionario_id=tesis_funcionario.id),
        )
    form.tesis.data = tesis_jurisprudencia.clave_control
    return render_template(
        "tesis_jurisprudencias_funcionarios/new_with_tesis.jinja2",
        form=form,
        tesis_jurisprudencia=tesis_jurisprudencia,
        titulo=f"Agregar funcionario",
    )


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios/eliminar/<int:tesis_jurisprudencia_funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(tesis_jurisprudencia_funcionario_id):
    """Eliminar Tesis-Jurisprudencias-Funcionario"""
    tesis_funcionario = TesisJurisprudenciaFuncionario.query.get_or_404(tesis_jurisprudencia_funcionario_id)
    if tesis_funcionario.estatus == "A":
        tesis_funcionario.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado tesis-jurisprudencia-funcionario {tesis_funcionario.funcionario.nombres}"),
            url=url_for("tesis_jurisprudencias_funcionarios.detail", tesis_jurisprudencia_funcionario_id=tesis_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("tesis_jurisprudencias_funcionarios.detail", tesis_jurisprudencia_funcionario_id=tesis_funcionario.id))


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios/recuperar/<int:tesis_jurisprudencia_funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(tesis_jurisprudencia_funcionario_id):
    """Tesis-Jurisprudencias-Funcionario"""
    tesis_funcionario = TesisJurisprudenciaFuncionario.query.get_or_404(tesis_jurisprudencia_funcionario_id)
    if tesis_funcionario.estatus == "B":
        tesis_funcionario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado tesis-jurisprudencias-funcionario {tesis_funcionario.funcionario.nombres}"),
            url=url_for("tesis_jurisprudencias_funcionarios.detail", tesis_jurisprudencia_funcionario_id=tesis_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("tesis_jurisprudencias_funcionarios.detail", tesis_jurisprudencia_funcionario_id=tesis_funcionario.id))


@tesis_jurisprudencias_funcionarios.route("/tesis_jurisprudencias_funcionarios/inactivos/<int:tesis_jurisprudencias_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive(tesis_jurisprudencias_id):
    """Listado de Tesis-Jurisprudencias-Funcionarios inactivos"""
    tesis_funcionarios_inactivos = TesisJurisprudenciaFuncionario.query.filter(TesisJurisprudenciaFuncionario.estatus == "B").filter(TesisJurisprudenciaFuncionario.tesis_jurisprudencias_id == tesis_jurisprudencias_id).all()
    return render_template(
        "tesis_jurisprudencias_funcionarios/list.jinja2",
        tesis_jurisprudencias_funcionarios=tesis_funcionarios_inactivos,
        titulo="Tesis-Jurisprudencias-Funcionarios inactivos",
        estatus="B",
    )
