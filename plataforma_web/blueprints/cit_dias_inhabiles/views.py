"""
CITAS Días Inhábiles, vistas
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_dias_inhabiles.models import CITDiaInhabil

from plataforma_web.blueprints.cit_dias_inhabiles.forms import CITDiasInhabilesForm

MODULO = "CIT DIAS INHABILES"

cit_dias_inhabiles = Blueprint("cit_dias_inhabiles", __name__, template_folder="templates")


@cit_dias_inhabiles.route("/cit_dias_inhabiles")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Días Inhábiles activos"""
    activos = CITDiaInhabil.query.filter(CITDiaInhabil.estatus == "A").all()
    return render_template(
        "cit_dias_inhabiles/list.jinja2",
        dias_inhabiles=activos,
        titulo="Días Inhábiles",
        estatus="A",
    )


@cit_dias_inhabiles.route("/cit_dias_inhabiles/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de cit_dias_inhabiles inactivos"""
    inactivos = CITDiaInhabil.query.filter(CITDiaInhabil.estatus == "B").all()
    return render_template(
        "cit_dias_inhabiles/list.jinja2",
        dias_inhabiles=inactivos,
        titulo="Días Inhábiles inactivos",
        estatus="B",
    )


@cit_dias_inhabiles.route("/cit_dias_inhabiles/<int:dia_inhabil_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(dia_inhabil_id):
    """Detalle de un Día Inhábil"""
    dia_inhabil = CITDiaInhabil.query.get_or_404(dia_inhabil_id)
    return render_template("cit_dias_inhabiles/detail.jinja2", dia_inhabil=dia_inhabil)

@cit_dias_inhabiles.route("/cit_dias_inhabiles/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo CITAS_Cliente"""
    form = CITDiasInhabilesForm()
    if form.validate_on_submit():
        dia_inhabil = CITDiaInhabil(
            fecha=form.fecha.data,
            descripcion=form.descripcion.data,
        )
        dia_inhabil.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Día Inhábil {dia_inhabil.fecha}"),
            url=url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("cit_dias_inhabiles/new.jinja2", form=form)


@cit_dias_inhabiles.route("/cit_dias_inhabiles/edicion/<int:dia_inhabil_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(dia_inhabil_id):
    """Editar Cliente, solo al escribir la contraseña se cambia"""
    dia_inhabil = CITDiaInhabil.query.get_or_404(dia_inhabil_id)
    form = CITDiasInhabilesForm()
    if form.validate_on_submit():
        dia_inhabil.fecha = form.fecha.data
        dia_inhabil.descripcion = form.descripcion.data
        dia_inhabil.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Día Inhábil {dia_inhabil.fecha}"),
            url=url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.fecha.data = dia_inhabil.fecha
    form.descripcion.data = dia_inhabil.descripcion
    return render_template("cit_dias_inhabiles/edit.jinja2", form=form, dia_inhabil=dia_inhabil)


@cit_dias_inhabiles.route("/cit_dias_inhabiles/eliminar/<int:dia_inhabil_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(dia_inhabil_id):
    """Eliminar Día Inhábil"""
    dia_inhabil = CITDiaInhabil.query.get_or_404(dia_inhabil_id)
    if dia_inhabil.estatus == "A":
        dia_inhabil.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la fecha {dia_inhabil.fecha}"),
            url=url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil_id))


@cit_dias_inhabiles.route("/cit_dias_inhabiles/recuperar/<int:dia_inhabil_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(dia_inhabil_id):
    """Recuperar cliente"""
    dia_inhabil = CITDiaInhabil.query.get_or_404(dia_inhabil_id)
    if dia_inhabil.estatus == "B":
        dia_inhabil.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada la fecha {dia_inhabil.fecha}"),
            url=url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_dias_inhabiles.detail", dia_inhabil_id=dia_inhabil_id))
