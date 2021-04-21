"""
Edictos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.edictos.forms import EdictoForm, EdictoSearchForm

edictos = Blueprint("edictos", __name__, template_folder="templates")


@edictos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """ Permiso por defecto """


@edictos.route("/edictos")
def list_active():
    """ Listado de Edictos activos """
    edictos_activos = Edicto.query.filter(Edicto.estatus == "A").order_by(Edicto.fecha.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", edictos=edictos_activos, estatus="A")


@edictos.route("/edictos/inactivos")
def list_inactive():
    """ Listado de Edictos inactivos """
    edictos_inactivos = Edicto.query.filter(Edicto.estatus == "B").order_by(Edicto.fecha.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", edictos=edictos_inactivos, estatus="B")


@edictos.route("/edictos/<int:edicto_id>")
def detail(edicto_id):
    """ Detalle de un Edicto """
    edicto = Edicto.query.get_or_404(edicto_id)
    return render_template("edictos/detail.jinja2", edicto=edicto)


@edictos.route("/edictos/buscar", methods=["GET", "POST"])
def search():
    """ Buscar Edictos """
    form_search = EdictoSearchForm()
    if form_search.validate_on_submit():
        consulta = Edicto.query
        if form_search.expediente.data:
            expediente = form_search.expediente.data.strip()
            consulta = consulta.filter(Edicto.expediente.like(f"%{expediente}%"))
        consulta = consulta.order_by(Edicto.fecha.desc()).limit(100).all()
        return render_template("edictos/list.jinja2", edictos=consulta)
    return render_template("edictos/search.jinja2", form=form_search)


@edictos.route("/edictos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """ Nuevo Edicto """
    form = EdictoForm()
    if form.validate_on_submit():
        edicto = Edicto(
            descripcion=form.descripcion.data,
            archivo=form.archivo.data,
            fecha=form.fecha.data,
            expediente=form.expediente.data,
            numero_publicacion=form.numero_publicacion.data,
            url=form.url.data,
        )
        edicto.save()
        flash(f"Edicto {edicto.descripcion} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))
    return render_template("edictos/new.jinja2", form=form)


@edictos.route("/edictos/edicion/<int:edicto_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit(edicto_id):
    """ Editar Edicto """
    edicto = Edicto.query.get_or_404(edicto_id)
    form = EdictoForm()
    if form.validate_on_submit():
        edicto.descripcion = form.descripcion.data
        edicto.archivo = form.archivo.data
        edicto.fecha = form.fecha.data
        edicto.expediente = form.expediente.data
        edicto.numero_publicacion = form.numero_publicacion.data
        edicto.url = form.url.data
        edicto.save()
        flash(f"Edicto {edicto.descripcion} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))
    form.descripcion.data = edicto.descripcion
    form.archivo.data = edicto.archivo
    form.fecha.data = edicto.fecha
    form.expediente.data = edicto.expediente
    form.numero_publicacion.data = edicto.numero_publicacion
    form.url.data = edicto.url
    return render_template("edictos/edit.jinja2", form=form, edicto=edicto)


@edictos.route("/edictos/eliminar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(edicto_id):
    """ Eliminar Edicto """
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "A":
        edicto.delete()
        flash(f"Edicto {edicto.Edicto} eliminado.", "success")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))


@edictos.route("/edictos/recuperar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(edicto_id):
    """ Recuperar Edicto """
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "B":
        edicto.recover()
        flash(f"Edicto {edicto.Edicto} recuperado.", "success")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))
