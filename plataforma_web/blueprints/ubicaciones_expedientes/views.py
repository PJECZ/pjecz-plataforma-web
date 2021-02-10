"""
Ubicacion de Expedientes, vistas
"""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente
from plataforma_web.blueprints.ubicaciones_expedientes.forms import UbicacionExpedienteForm

ubicaciones_expedientes = Blueprint("ubicaciones_expedientes", __name__, template_folder="templates")


@ubicaciones_expedientes.before_request
@login_required
@permission_required(Permiso.VER_CONTENIDOS)
def before_request():
    """ Permiso por defecto """


@ubicaciones_expedientes.route("/ubicaciones_expedientes")
def list_active():
    """ Listado de Ubicaciones de Expedientes """
    ubicaciones_expedientes_activos = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "A").all()
    return render_template("ubicaciones_expedientes/list.jinja2", ubicaciones_expedientes=ubicaciones_expedientes_activos)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/<int:ubicacion_expediente_id>")
def detail(ubicacion_expediente_id):
    """ Detalle de una Ubicacion de Expediente """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    return render_template("ubicaciones_expedientes/detail.jinja2", ubicacion_expediente=ubicacion_expediente)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONTENIDOS)
def new():
    """ Nuevo Ubicación de Expedientes """
    form = UbicacionExpedienteForm()
    if form.validate_on_submit():
        ubicacion_expediente = UbicacionExpediente(
            expediente=form.expediente.data,
            ubicacion=form.ubicacion.data,
        )
        ubicacion_expediente.save()
        flash(f"Ubicación de Expedientes {ubicacion_expediente.expediente} guardado.", "success")
        return redirect(url_for("ubicaciones_expedientes.list_active"))
    return render_template("ubicaciones_expedientes/new.jinja2", form=form)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/edicion/<int:ubicacion_expediente_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONTENIDOS)
def edit(ubicacion_expediente_id):
    """ Editar Ubicación de Expedientes """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    form = UbicacionExpedienteForm()
    if form.validate_on_submit():
        ubicacion_expediente.expediente = form.expediente.data
        ubicacion_expediente.ubicacion = form.ubicacion.data
        ubicacion_expediente.save()
        flash(f"Ubicación de Expedientes {ubicacion_expediente.expediente} guardado.", "success")
        return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id))
    form.expediente.data = ubicacion_expediente.expediente
    form.ubicacion.data = ubicacion_expediente.ubicacion
    return render_template("ubicaciones_expedientes/edit.jinja2", form=form, ubicacion_expediente=ubicacion_expediente)
