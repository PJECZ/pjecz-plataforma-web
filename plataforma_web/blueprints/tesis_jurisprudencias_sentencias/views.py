"""
Tesis uriesprudencias Sentencias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia
from plataforma_web.blueprints.tesis_jurisprudencias_sentencias.models import TesisJurisprudenciaSentencia
from plataforma_web.blueprints.tesis_jurisprudencias_sentencias.forms import TesisSentenciaWithTesisForm

MODULO = "TESIS JURISPRUDENCIAS"

tesis_jurisprudencias_sentencias = Blueprint("tesis_jurisprudencias_sentencias", __name__, template_folder="templates")


@tesis_jurisprudencias_sentencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias/<int:tesis_jurisprudencia_sentencia_id>")
def detail(tesis_jurisprudencia_sentencia_id):
    """Detalle de una Tesis-Jurisprudencia Sentencias"""
    tesis_jurisprudencia_sentencia = TesisJurisprudenciaSentencia.query.get_or_404(tesis_jurisprudencia_sentencia_id)
    return render_template("tesis_jurisprudencias_sentencias/detail.jinja2", tesis_jurisprudencia_sentencia=tesis_jurisprudencia_sentencia)




@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias")
def list_active():
    """Listado de Sentencias de una Tesis o Jurisprudencia"""
    sentencias_activos = TesisJurisprudenciaSentencia.query.filter(TesisJurisprudenciaSentencia.estatus == "A").all()
    return render_template(
        "tesis_jurisprudencias_sentencias/list.jinja2",
        tesis_jurisprudencias_sentencias=sentencias_activos,
        titulo="Sentencias de una Tesis y Jurisprudencia",
        estatus="A",
    )

@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias/nuevo_con_tesis/<int:tesis_jurisprudencias_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_tesis(tesis_jurisprudencias_id):
    """Nuevo Tesis-Sentencia con Tesis"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencias_id)
    form = TesisSentenciaWithTesisForm()
    if form.validate_on_submit():
        sentencia = form.sentencia.data
        descripcion = f"{sentencia.sentencia} en {tesis_jurisprudencia.clave_control} "
        if TesisJurisprudenciaSentencia.query.filter(TesisJurisprudenciaSentencia.tesis_jurisprudencia_id == tesis_jurisprudencias_id).filter(TesisJurisprudenciaSentencia.sentencia_id == sentencia.id).first() is not None:
            flash(f"CONFLICTO: Ya existe el Sentencia {descripcion}. Mejor recupere el registro.", "warning")
            return redirect(url_for("tesis_jurisprudencias_sentencias.list_inactive", tesis_jurisprudencias_id=tesis_jurisprudencias_id))
        tesis_sentencia= TesisJurisprudenciaSentencia(
            sentencia=sentencia,
            tesis_jurisprudencia=tesis_jurisprudencia,

        )        
        tesis_sentencia.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva sentencia en tesis-jurisprudencia-sentencia {tesis_sentencia.sentencia.sentencia}"),
            url=url_for("tesis_jurisprudencias_sentencias.detail", tesis_jurisprudencia_sentencia_id=tesis_sentencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.tesis.data = tesis_jurisprudencia.clave_control
    return render_template(
        "tesis_jurisprudencias_sentencias/new_with_tesis.jinja2",
        form=form,
        tesis_jurisprudencia=tesis_jurisprudencia,
        titulo=f"Agregar sentencia",
    )

@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias/inactivos/<int:tesis_jurisprudencias_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive(tesis_jurisprudencias_id):
    """Listado de Tesis-Jurisprudencias-Sentencias inactivos"""
    tesis_sentencias_inactivos = TesisJurisprudenciaSentencia.query.filter(TesisJurisprudenciaSentencia.estatus == "B").filter(TesisJurisprudenciaSentencia.tesis_jurisprudencia_id == tesis_jurisprudencias_id).all()
    return render_template(
        "tesis_jurisprudencias_sentencias/list.jinja2",
        tesis_jurisprudencias_sentencias=tesis_sentencias_inactivos,
        titulo="Tesis-Jurisprudencias-Sentencias inactivos",
        estatus="B",
    )

@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias/eliminar/<int:tesis_jurisprudencia_sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(tesis_jurisprudencia_sentencia_id):
    """Eliminar Tesis-Jurisprudencias-Sentencias"""
    tesis_sentencia = TesisJurisprudenciaSentencia.query.get_or_404(tesis_jurisprudencia_sentencia_id)
    if tesis_sentencia.estatus == "A":
        tesis_sentencia.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado tesis-jurisprudencia-sentencia {tesis_sentencia.sentencia.sentencia}"),
            url=url_for("tesis_jurisprudencias_sentencias.detail", tesis_jurisprudencia_sentencia_id=tesis_sentencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("tesis_jurisprudencias_sentencias.detail", tesis_jurisprudencia_sentencia_id=tesis_sentencia.id))

@tesis_jurisprudencias_sentencias.route("/tesis_jurisprudencias_sentencias/recuperar/<int:tesis_jurisprudencia_sentencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(tesis_jurisprudencia_sentencia_id):
    """Tesis-Jurisprudencias-Sentencia"""
    tesis_sentencia = TesisJurisprudenciaSentencia.query.get_or_404(tesis_jurisprudencia_sentencia_id)
    if tesis_sentencia.estatus == "B":
        tesis_sentencia.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado tesis-jurisprudencias-funcionario {tesis_sentencia.sentencia.sentencia}"),
            url=url_for("tesis_jurisprudencias_sentencias.detail", tesis_jurisprudencia_sentencia_id=tesis_sentencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("tesis_jurisprudencias_sentencias.detail", tesis_jurisprudencia_sentencia_id=tesis_sentencia.id))


