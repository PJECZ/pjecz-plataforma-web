"""
CITAS Días Inhábiles, vistas
"""

import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.cit_servicios.models import CITServicio

from plataforma_web.blueprints.cit_servicios.forms import CITServiciosForm

MODULO = "CIT SERVICIOS"

cit_servicios = Blueprint("cit_servicios", __name__, template_folder="templates")


@cit_servicios.route("/cit_servicios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Servicios activos"""
    activos = CITServicio.query.filter(CITServicio.estatus == "A").all()
    return render_template(
        "cit_servicios/list.jinja2",
        servicios=activos,
        titulo="Servicios",
        estatus="A",
    )


@cit_servicios.route("/cit_servicios/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Servicios inactivos"""
    inactivos = CITServicio.query.filter(CITServicio.estatus == "B").all()
    return render_template(
        "cit_servicios/list.jinja2",
        servicios=inactivos,
        titulo="Servicios inactivos",
        estatus="B",
    )


@cit_servicios.route("/cit_servicios/<int:servicio_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(servicio_id):
    """Detalle de un Servicio"""
    servicio = CITServicio.query.get_or_404(servicio_id)
    return render_template("cit_servicios/detail.jinja2", servicio=servicio)


@cit_servicios.route("/cit_servicios/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Servicio"""
    form = CITServiciosForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar(form)
            validacion = True
        except Exception as err:
            flash(f"Creación del nuevo Servicio incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            servicio = CITServicio(
                clave=form.clave.data.upper(),
                nombre=form.nombre.data,
                solicitar_expedientes=form.solicitar_expedientes.data,
                duracion=form.duracion.data,
            )
            servicio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Servicio {servicio.clave}"),
                url=url_for("cit_servicios.detail", servicio_id=servicio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("cit_servicios/new.jinja2", form=form)


@cit_servicios.route("/cit_servicios/edicion/<int:servicio_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(servicio_id):
    """Editar Servicio"""
    servicio = CITServicio.query.get_or_404(servicio_id)
    form = CITServiciosForm()
    validacion = False
    if form.validate_on_submit():

        try:
            _validar(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización incorrecta del servicio. {str(err)}", "warning")
            validacion = False

        if validacion:
            servicio.clave = form.clave.data.upper()
            servicio.nombre = form.nombre.data
            servicio.solicitar_expedientes = form.solicitar_expedientes.data
            servicio.duracion = form.duracion.data
            servicio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado el Servicio {servicio.clave}"),
                url=url_for("cit_servicios.detail", servicio_id=servicio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = servicio.clave
    form.nombre.data = servicio.nombre
    form.solicitar_expedientes.data = servicio.solicitar_expedientes
    form.duracion.data = servicio.duracion
    return render_template("cit_servicios/edit.jinja2", form=form, servicio=servicio)


def _validar(form, same=False):
    if not same:
        clave_existente = CITServicio.query.filter(CITServicio.clave == form.clave.data).first()
        if clave_existente:
            raise Exception("La clave ya se encuentra en uso.")
    min_duracion = datetime.time(0, 15, 0)
    if form.duracion.data < min_duracion:
        min_duracion = min_duracion.strftime("%H:%M")
        raise Exception(f"La duración del servicio es muy poco, lo mínimno permitido son: {min_duracion}")
    max_duracion = datetime.time(8, 0, 0)
    if form.duracion.data > max_duracion:
        max_duracion = max_duracion.strftime("%H:%M")
        raise Exception(f"La duración del servicio es mucho, lo máximo permitido son: {max_duracion}")
    return True


@cit_servicios.route("/cit_servicios/eliminar/<int:servicio_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(servicio_id):
    """Eliminar Servicio"""
    servicio = CITServicio.query.get_or_404(servicio_id)
    if servicio.estatus == "A":
        servicio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el servicio {servicio.clave}"),
            url=url_for("cit_servicios.detail", servicio_id=servicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_servicios.detail", servicio_id=servicio_id))


@cit_servicios.route("/cit_servicios/recuperar/<int:servicio_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(servicio_id):
    """Recuperar Servicio"""
    servicio = CITServicio.query.get_or_404(servicio_id)
    if servicio.estatus == "B":
        servicio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el Servicio {servicio.clave}"),
            url=url_for("cit_servicios.detail", servicio_id=servicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_servicios.detail", servicio_id=servicio_id))
