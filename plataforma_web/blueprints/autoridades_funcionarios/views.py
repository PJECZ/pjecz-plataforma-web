"""
Autoridades Funcionarios, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.autoridades_funcionarios.models import AutoridadFuncionario
from plataforma_web.blueprints.autoridades_funcionarios.forms import AutoridadFuncionarioForm, AutoridadFuncionarioWithAutoridadForm, AutoridadFuncionarioWithFuncionarioForm

MODULO = "AUTORIDADES FUNCIONARIOS"

autoridades_funcionarios = Blueprint("autoridades_funcionarios", __name__, template_folder="templates")


@autoridades_funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades_funcionarios.route("/autoridades_funcionarios")
def list_active():
    """Listado de Autoridades-Funcionarios activos"""
    autoridades_funcionarios_activos = AutoridadFuncionario.query.filter(AutoridadFuncionario.estatus == "A").all()
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        autoridades_funcionarios=autoridades_funcionarios_activos,
        titulo="Autoridades-Funcionarios",
        estatus="A",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades-Funcionarios inactivos"""
    autoridades_funcionarios_inactivos = AutoridadFuncionario.query.filter(AutoridadFuncionario.estatus == "B").all()
    return render_template(
        "autoridades_funcionarios/list.jinja2",
        autoridades_funcionarios=autoridades_funcionarios_inactivos,
        titulo="Autoridades-Funcionarios inactivos",
        estatus="B",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/<int:autoridad_funcionario_id>")
def detail(autoridad_funcionario_id):
    """Detalle de un Autoridad-Funcionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    return render_template("autoridades_funcionarios/detail.jinja2", autoridad_funcionario=autoridad_funcionario)


@autoridades_funcionarios.route("/autoridades_funcionarios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Autoridad-Funcionario"""
    form = AutoridadFuncionarioForm()
    if form.validate_on_submit():
        autoridad = form.autoridad.data
        funcionario = form.funcionario.data
        descripcion = f"{funcionario.nombre} en {autoridad.clave}"
        if AutoridadFuncionario.query.filter(AutoridadFuncionario.autoridad == autoridad).filter(AutoridadFuncionario.funcionario == funcionario).first() is not None:
            flash(f"CONFLICTO: Ya existe {descripcion}. Mejor recupere el registro.", "warning")
            return redirect(url_for("autoridades_funcionarios.list_inactive"))
        autoridad_funcionario = AutoridadFuncionario(
            autoridad=autoridad,
            funcionario=funcionario,
            descripcion=descripcion,
        )
        autoridad_funcionario.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo autoridad-funcionario {autoridad_funcionario.descripcion}"),
            url=url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template(
        "autoridades_funcionarios/new.jinja2",
        form=form,
        titulo="Nuevo Autoridad-Funcionario",
    )


@autoridades_funcionarios.route("/autoridades_funcionarios/nuevo_con_autoridad/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_autoridad(autoridad_id):
    """Nuevo Autoridad-Funcionario con Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadFuncionarioWithAutoridadForm()
    if form.validate_on_submit():
        funcionario = form.funcionario.data
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
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo autoridad-funcionario {autoridad_funcionario.descripcion}"),
            url=url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.autoridad.data = autoridad.clave
    return render_template(
        "autoridades_funcionarios/new_with_autoridad.jinja2",
        form=form,
        autoridad=autoridad,
        titulo=f"Agregar funcionario a la autoridad {autoridad.clave}",
    )


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
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo autoridad-funcionario {autoridad_funcionario.descripcion}"),
            url=url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
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
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado autoridad-funcionario {autoridad_funcionario.descripcion}"),
            url=url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridades_funcionarios.id))


@autoridades_funcionarios.route("/autoridades_funcionarios/recuperar/<int:autoridad_funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(autoridad_funcionario_id):
    """Recuperar Autoridad-Funcionario"""
    autoridad_funcionario = AutoridadFuncionario.query.get_or_404(autoridad_funcionario_id)
    if autoridad_funcionario.estatus == "B":
        autoridad_funcionario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado autoridad-funcionario {autoridad_funcionario.descripcion}"),
            url=url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades_funcionarios.detail", autoridad_funcionario_id=autoridad_funcionario.id))
