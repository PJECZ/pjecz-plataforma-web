"""
Abogados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from unidecode import unidecode
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.abogados.models import Abogado
from plataforma_web.blueprints.abogados.forms import AbogadoForm, AbogadoSearchForm

abogados = Blueprint("abogados", __name__, template_folder="templates")


@abogados.before_request
@login_required
@permission_required(Permiso.VER_CONSULTAS)
def before_request():
    """ Permiso por defecto """


@abogados.route("/abogados")
def list_active():
    """ Listado de Abogados activos """
    abogados_activos = Abogado.query.filter(Abogado.estatus == "A").order_by(Abogado.fecha.desc()).limit(100).all()
    return render_template("abogados/list.jinja2", abogados=abogados_activos, estatus="A")


@abogados.route("/abogados/inactivos")
def list_inactive():
    """ Listado de Abogados inactivos """
    abogados_inactivos = Abogado.query.filter(Abogado.estatus == "B").order_by(Abogado.fecha.desc()).limit(100).all()
    return render_template("abogados/list.jinja2", abogados=abogados_inactivos, estatus="B")


@abogados.route("/abogados/<int:abogado_id>")
def detail(abogado_id):
    """ Detalle de un Abogado """
    abogado = Abogado.query.get_or_404(abogado_id)
    return render_template("abogados/detail.jinja2", abogado=abogado)


@abogados.route("/abogados/buscar", methods=["GET", "POST"])
def search():
    """ Buscar Abogados """
    form_search = AbogadoSearchForm()
    if form_search.validate_on_submit():
        consulta = Abogado.query
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Abogado.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Abogado.fecha <= form_search.fecha_hasta.data)
        if form_search.numero.data:
            numero = unidecode(form_search.numero.data).upper()  # Sin acentos y en mayúsculas
            consulta = consulta.filter(Abogado.numero == numero)
        if form_search.libro.data:
            libro = unidecode(form_search.libro.data).upper()  # Sin acentos y en mayúsculas
            consulta = consulta.filter(Abogado.libro == libro)
        if form_search.nombre.data:
            nombre = unidecode(form_search.nombre.data.strip()).upper()  # Sin acentos y en mayúsculas
            consulta = consulta.filter(Abogado.nombre.like(f"%{nombre}%"))
        consulta = consulta.order_by(Abogado.fecha.desc()).limit(100).all()
        return render_template("abogados/list.jinja2", abogados=consulta)
    return render_template("abogados/search.jinja2", form=form_search)


@abogados.route("/abogados/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONSULTAS)
def new():
    """ Nuevo Abogado """
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado = Abogado(
            numero=form.numero.data.strip(),
            nombre=unidecode(form.nombre.data.strip()).upper(),  # Sin acentos y en mayúsculas
            libro=form.libro.data.strip(),
            fecha=form.fecha.data,
        )
        abogado.save()
        flash(f"Abogado {abogado.nombre} guardado.", "success")
        return redirect(url_for("abogados.detail", abogado_id=abogado.id))
    return render_template("abogados/new.jinja2", form=form)


@abogados.route("/abogados/edicion/<int:abogado_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def edit(abogado_id):
    """ Editar Abogado """
    abogado = Abogado.query.get_or_404(abogado_id)
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado.numero = form.numero.data.strip()
        abogado.nombre = unidecode(form.nombre.data.strip()).upper()  # Sin acentos y en mayúsculas
        abogado.libro = form.libro.data.strip()
        abogado.fecha = form.fecha.data
        abogado.save()
        flash(f"Abogado {abogado.nombre} guardado.", "success")
        return redirect(url_for("abogados.detail", abogado_id=abogado.id))
    form.numero.data = abogado.numero
    form.nombre.data = abogado.nombre
    form.libro.data = abogado.libro
    form.fecha.data = abogado.fecha
    return render_template("abogados/edit.jinja2", form=form, abogado=abogado)


@abogados.route("/abogados/eliminar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def delete(abogado_id):
    """ Eliminar Abogado """
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "A":
        abogado.delete()
        flash(f"Abogado {abogado.nombre} eliminado.", "success")
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))


@abogados.route("/abogados/recuperar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def recover(abogado_id):
    """ Recuperar Abogado """
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "B":
        abogado.recover()
        flash(f"Abogado {abogado.nombre} recuperado.", "success")
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))
