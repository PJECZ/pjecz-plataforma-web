"""
Ubicacion de Expedientes, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente
from plataforma_web.blueprints.ubicaciones_expedientes.forms import UbicacionExpedienteNewForm, UbicacionExpedienteEditForm, UbicacionExpedienteSearchForm
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

ubicaciones_expedientes = Blueprint("ubicaciones_expedientes", __name__, template_folder="templates")


@ubicaciones_expedientes.before_request
@login_required
@permission_required(Permiso.VER_CONSULTAS)
def before_request():
    """ Permiso por defecto """


@ubicaciones_expedientes.route("/ubicaciones_expedientes")
def list_active():
    """ Listado de Ubicaciones de Expedientes """
    ubicaciones_expedientes_activos = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "A").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
    return render_template("ubicaciones_expedientes/list.jinja2", ubicaciones_expedientes=ubicaciones_expedientes_activos, estatus="A")


@ubicaciones_expedientes.route("/ubicaciones_expedientes/inactivos")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def list_inactive():
    """ Listado de Ubicaciones de Expedientes inactivos """
    ubicaciones_expedientes_inactivos = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "B").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
    return render_template("ubicaciones_expedientes/list.jinja2", ubicaciones_expedientes=ubicaciones_expedientes_inactivos, estatus="B")


@ubicaciones_expedientes.route("/ubicaciones_expedientes/<int:ubicacion_expediente_id>")
def detail(ubicacion_expediente_id):
    """ Detalle de una Ubicacion de Expediente """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    return render_template("ubicaciones_expedientes/detail.jinja2", ubicacion_expediente=ubicacion_expediente)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/buscar", methods=["GET", "POST"])
def search():
    """ Buscar Ubicacion de Expediente """
    form_search = UbicacionExpedienteSearchForm()
    if form_search.validate_on_submit():
        consulta = UbicacionExpediente.query
        if form_search.expediente.data:
            expediente = form_search.expediente.data.strip()
            consulta = consulta.filter(UbicacionExpediente.expediente.like(f"%{expediente}%"))
        consulta = consulta.order_by(UbicacionExpediente.creado.desc()).limit(100).all()
        return render_template("ubicaciones_expedientes/list.jinja2", ubicaciones_expedientes=consulta)
    return render_template("ubicaciones_expedientes/search.jinja2", form=form_search)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONSULTAS)
def new():
    """ Nuevo Ubicación de Expedientes """
    form = UbicacionExpedienteNewForm()
    if form.validate_on_submit():
        ubicacion_expediente = UbicacionExpediente(
            autoridad=Autoridad.query.get_or_404(form.autoridad.data),
            expediente=form.expediente.data.strip(),
            ubicacion=form.ubicacion.data,
        )
        ubicacion_expediente.save()
        flash(f"Ubicación de Expedientes {ubicacion_expediente.expediente} guardado.", "success")
        return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id))
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("ubicaciones_expedientes/new.jinja2", form=form, distritos=distritos, autoridades=autoridades)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/edicion/<int:ubicacion_expediente_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def edit(ubicacion_expediente_id):
    """ Editar Ubicación de Expedientes """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    form = UbicacionExpedienteEditForm()
    if form.validate_on_submit():
        ubicacion_expediente.autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        ubicacion_expediente.expediente = form.expediente.data.strip()
        ubicacion_expediente.ubicacion = form.ubicacion.data
        ubicacion_expediente.save()
        flash(f"Ubicación de Expedientes {ubicacion_expediente.expediente} guardado.", "success")
        return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id))
    form.distrito.data = ubicacion_expediente.autoridad.distrito.nombre
    form.autoridad.data = ubicacion_expediente.autoridad.descripcion
    form.expediente.data = ubicacion_expediente.expediente
    form.ubicacion.data = ubicacion_expediente.ubicacion
    return render_template("ubicaciones_expedientes/edit.jinja2", form=form, ubicacion_expediente=ubicacion_expediente)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/eliminar/<int:ubicacion_expediente_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def delete(ubicacion_expediente_id):
    """ Eliminar Ubicacion de Expedientes """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    if ubicacion_expediente.estatus == "A":
        ubicacion_expediente.delete()
        flash(f"Ubicacion de Expediente {ubicacion_expediente.expediente} eliminado.", "success")
    return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente_id))


@ubicaciones_expedientes.route("/ubicaciones_expedientes/recuperar/<int:ubicacion_expediente_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def recover(ubicacion_expediente_id):
    """ Recuperar Lista de Acuerdos """
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    if ubicacion_expediente.estatus == "B":
        ubicacion_expediente.recover()
        flash(f"Ubicacion de Expediente {ubicacion_expediente.expediente} recuperado.", "success")
    return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente_id))
