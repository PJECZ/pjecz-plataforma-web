"""
REPSVM Tipos de Sentencias, vistas
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
from plataforma_web.blueprints.repsvm_tipos_sentencias.models import REPSVMTipoSentencia
from plataforma_web.blueprints.repsvm_tipos_sentencias.forms import REPSVMTipoSentenciaForm

MODULO = "REPSVM TIPOS SENTENCIAS"

repsvm_tipos_sentencias = Blueprint("repsvm_tipos_sentencias", __name__, template_folder="templates")


@repsvm_tipos_sentencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias")
def list_active():
    """Listado de Tipos de Sentencias activos"""
    repsvm_tipos_sentencias_activos = REPSVMTipoSentencia.query.filter(REPSVMTipoSentencia.estatus == "A").all()
    return render_template(
        "repsvm_tipos_sentencias/list.jinja2",
        repsvm_tipos_sentencias=repsvm_tipos_sentencias_activos,
        titulo="Tipos de Sentencias",
        estatus="A",
    )


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tipos de Sentencias inactivos"""
    repsvm_tipos_sentencias_inactivos = REPSVMTipoSentencia.query.filter(REPSVMTipoSentencia.estatus == "B").all()
    return render_template(
        "repsvm_tipos_sentencias/list.jinja2",
        repsvm_tipos_sentencias=repsvm_tipos_sentencias_inactivos,
        titulo="Tipos de Sentencias inactivos",
        estatus="B",
    )


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/<int:repsvm_tipo_sentencia_id>")
def detail(repsvm_tipo_sentencia_id):
    """Detalle de un Tipo de Sentencia"""
    repsvm_tipo_sentencia = REPSVMTipoSentencia.query.get_or_404(repsvm_tipo_sentencia_id)
    return render_template("repsvm_tipos_sentencias/detail.jinja2", repsvm_tipo_sentencia=repsvm_tipo_sentencia)


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Tipo de Sentencia"""
    form = REPSVMTipoSentenciaForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if REPSVMTipoSentencia.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
        else:
            repsvm_tipo_sentencia = REPSVMTipoSentencia(nombre=nombre)
            repsvm_tipo_sentencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Tipo de Sentencia {repsvm_tipo_sentencia.nombre}"),
                url=url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=repsvm_tipo_sentencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("repsvm_tipos_sentencias/new.jinja2", form=form)


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/edicion/<int:repsvm_tipo_sentencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_tipo_sentencia_id):
    """Editar Tipo de Sentencia"""
    repsvm_tipo_sentencia = REPSVMTipoSentencia.query.get_or_404(repsvm_tipo_sentencia_id)
    form = REPSVMTipoSentenciaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if repsvm_tipo_sentencia.nombre != nombre:
            repsvm_tipo_sentencia_existente = REPSVMTipoSentencia.query.filter_by(nombre=nombre).first()
            if repsvm_tipo_sentencia_existente and repsvm_tipo_sentencia_existente.id != repsvm_tipo_sentencia_id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            repsvm_tipo_sentencia.nombre = nombre
            repsvm_tipo_sentencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Tipo de Sentencia {repsvm_tipo_sentencia.nombre}"),
                url=url_for("repsvm_tipos_sentencias.detail", repsvm_id=repsvm_tipo_sentencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = repsvm.nombre
    return render_template("repsvm_tipos_sentencias/edit.jinja2", form=form, repsvm=repsvm)


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/eliminar/<int:repsvm_tipo_sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(repsvm_tipo_sentencia_id):
    """Eliminar Tipo de Sentencia"""
    repsvm_tipo_sentencia = REPSVMTipoSentencia.query.get_or_404(repsvm_tipo_sentencia_id)
    if repsvm_tipo_sentencia.estatus == "A":
        repsvm_tipo_sentencia.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Tipo de Sentencia {repsvm_tipo_sentencia.nombre}"),
            url=url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=repsvm_tipo_sentencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=repsvm_tipo_sentencia.id))


@repsvm_tipos_sentencias.route("/repsvm_tipos_sentencias/recuperar/<int:repsvm_tipo_sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(repsvm_tipo_sentencia_id):
    """Recuperar Tipo de Sentencia"""
    repsvm_tipo_sentencia = REPSVMTipoSentencia.query.get_or_404(repsvm_tipo_sentencia_id)
    if repsvm_tipo_sentencia.estatus == "B":
        repsvm_tipo_sentencia.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Tipo de Sentencia {repsvm_tipo_sentencia.nombre}"),
            url=url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=repsvm_tipo_sentencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=repsvm_tipo_sentencia.id))
