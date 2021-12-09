"""
Funcionarios, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.funcionarios.forms import FuncionarioForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "FUNCIONARIOS"

funcionarios = Blueprint("funcionarios", __name__, template_folder="templates")


@funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@funcionarios.route("/funcionarios")
def list_active():
    """Listado de Funcionarios activos"""
    funcionarios_activos = Funcionario.query.filter(Funcionario.estatus == "A").all()
    return render_template(
        "funcionarios/list.jinja2",
        funcionarios=funcionarios_activos,
        titulo="Funcionarios",
        estatus="A",
    )


@funcionarios.route("/funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Funcionarios inactivos"""
    funcionarios_inactivos = Funcionario.query.filter(Funcionario.estatus == "B").all()
    return render_template(
        "funcionarios/list.jinja2",
        funcionarios=funcionarios_inactivos,
        titulo="Funcionarios inactivos",
        estatus="B",
    )


@funcionarios.route("/funcionarios/<int:funcionario_id>")
def detail(funcionario_id):
    """Detalle de un Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    return render_template("funcionarios/detail.jinja2", funcionario=funcionario)


@funcionarios.route("/funcionarios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Funcionario"""
    form = FuncionarioForm()
    if form.validate_on_submit():
        es_valido = True
        curp = safe_string(form.curp.data)
        if Funcionario.query.filter_by(curp=curp).first():
            flash(f"Ya existe un funcionario con la CURP {curp}", "warning")
            es_valido = False
        email = form.email.data
        if Funcionario.query.filter_by(email=email).first():
            flash(f"Ya existe un funcionario con el email {email}", "warning")
            es_valido = False
        if es_valido:
            funcionario = Funcionario(
                nombres=safe_string(form.nombres.data),
                apellido_paterno=safe_string(form.apellido_paterno.data),
                apellido_materno=safe_string(form.apellido_materno.data),
                curp=curp,
                email=email,
                puesto=safe_string(form.puesto.data),
                en_funciones=form.en_funciones.data,
                en_sentencias=form.en_sentencias.data,
                en_soportes=form.en_soportes.data,
                en_tesis_jurisprudencias=form.en_tesis_jurisprudencias.data,
            )
            funcionario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo funcionario {funcionario.nombre}"),
                url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("funcionarios/new.jinja2", form=form)


@funcionarios.route("/funcionarios/edicion/<int:funcionario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(funcionario_id):
    """Editar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    form = FuncionarioForm()
    if form.validate_on_submit():
        es_valido = True
        curp = safe_string(form.curp.data)
        if Funcionario.query.filter_by(curp=curp).filter(Funcionario.id != funcionario_id).first():
            flash(f"Ya existe un funcionario con la CURP {curp}", "warning")
            es_valido = False
        email = form.email.data
        if Funcionario.query.filter_by(email=email).filter(Funcionario.id != funcionario_id).first():
            flash(f"Ya existe un funcionario con el email {email}", "warning")
            es_valido = False
        if es_valido:
            funcionario.nombres = safe_string(form.nombres.data)
            funcionario.apellido_paterno = safe_string(form.apellido_paterno.data)
            funcionario.apellido_materno = safe_string(form.apellido_materno.data)
            funcionario.curp = curp
            funcionario.email = email
            funcionario.puesto = safe_string(form.puesto.data)
            funcionario.en_funciones = form.en_funciones.data
            funcionario.en_sentencias = form.en_sentencias.data
            funcionario.en_soportes = form.en_soportes.data
            funcionario.en_tesis_jurisprudencias = form.en_tesis_jurisprudencias.data
            funcionario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado funcionario {funcionario.nombre}"),
                url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombres.data = funcionario.nombres
    form.apellido_paterno.data = funcionario.apellido_paterno
    form.apellido_materno.data = funcionario.apellido_materno
    form.curp.data = funcionario.curp
    form.email.data = funcionario.email
    form.puesto.data = funcionario.puesto
    form.en_funciones.data = funcionario.en_funciones
    form.en_sentencias.data = funcionario.en_sentencias
    form.en_soportes.data = funcionario.en_soportes
    form.en_tesis_jurisprudencias.data = funcionario.en_tesis_jurisprudencias
    return render_template("funcionarios/edit.jinja2", form=form, funcionario=funcionario)


@funcionarios.route("/funcionarios/eliminar/<int:funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(funcionario_id):
    """Eliminar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario.estatus == "A":
        funcionario.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado funcionario {funcionario.nombre}"),
            url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("funcionarios.detail", funcionario_id=funcionario.id))


@funcionarios.route("/funcionarios/recuperar/<int:funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(funcionario_id):
    """Recuperar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario.estatus == "B":
        funcionario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado {funcionario.nombre}"),
            url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("funcionarios.detail", funcionario_id=funcionario.id))
