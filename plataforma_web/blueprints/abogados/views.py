"""
Abogados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.abogados.models import Abogado
from plataforma_web.blueprints.abogados.forms import AbogadoForm, AbogadoSearchForm
from plataforma_web.blueprints.bitacoras.models import Bitacora

abogados = Blueprint("abogados", __name__, template_folder="templates")
MODULO = "ABOGADOS"

@abogados.before_request
@login_required
@permission_required(Permiso.VER_CONSULTAS)
def before_request():
    """Permiso por defecto"""


@abogados.route("/abogados")
def list_active():
    """Listado de Abogados activos"""
    abogados_activos = Abogado.query.filter(Abogado.estatus == "A").order_by(Abogado.fecha.desc()).limit(100).all()
    return render_template("abogados/list.jinja2", abogados=abogados_activos, estatus="A")


@abogados.route("/abogados/inactivos")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def list_inactive():
    """Listado de Abogados inactivos"""
    abogados_inactivos = Abogado.query.filter(Abogado.estatus == "B").order_by(Abogado.fecha.desc()).limit(100).all()
    return render_template("abogados/list.jinja2", abogados=abogados_inactivos, estatus="B")


@abogados.route("/abogados/<int:abogado_id>")
def detail(abogado_id):
    """Detalle de un Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    return render_template("abogados/detail.jinja2", abogado=abogado)


@abogados.route("/abogados/buscar", methods=["GET", "POST"])
def search():
    """Buscar Abogados"""
    form_search = AbogadoSearchForm()
    if form_search.validate_on_submit():
        consulta = Abogado.query
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Abogado.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Abogado.fecha <= form_search.fecha_hasta.data)
        if form_search.numero.data:
            numero = safe_string(form_search.numero.data)
            consulta = consulta.filter(Abogado.numero == numero)
        if form_search.libro.data:
            libro = safe_string(form_search.libro.data)
            consulta = consulta.filter(Abogado.libro == libro)
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data)
            consulta = consulta.filter(Abogado.nombre.like(f"%{nombre}%"))
        consulta = consulta.order_by(Abogado.fecha.desc()).limit(100).all()
        return render_template("abogados/list.jinja2", abogados=consulta)
    return render_template("abogados/search.jinja2", form=form_search)


@abogados.route("/abogados/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONSULTAS)
def new():
    """Nuevo Abogado"""
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado = Abogado(
            numero=safe_string(form.numero.data),
            nombre=safe_string(form.nombre.data),
            libro=safe_string(form.libro.data),
            fecha=form.fecha.data,
        )
        abogado.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nuevo abogado registrado {abogado.nombre} con número {abogado.numero}"),
            url=url_for("abogados.detail", abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("abogados/new.jinja2", form=form)


@abogados.route("/abogados/edicion/<int:abogado_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def edit(abogado_id):
    """Editar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado.numero = safe_string(form.numero.data)
        abogado.nombre = safe_string(form.nombre.data)
        abogado.libro = safe_string(form.libro.data)
        abogado.fecha = form.fecha.data
        abogado.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Editado abogado registrado {abogado.nombre}'),
            url=url_for('abogados.detail', abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)
    form.numero.data = abogado.numero
    form.nombre.data = abogado.nombre
    form.libro.data = abogado.libro
    form.fecha.data = abogado.fecha
    return render_template("abogados/edit.jinja2", form=form, abogado=abogado)


@abogados.route("/abogados/eliminar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def delete(abogado_id):
    """Eliminar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "A":
        abogado.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Eliminado abogado registrado {abogado.nombre}'),
            url=url_for('abogados.detail', abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))


@abogados.route("/abogados/recuperar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def recover(abogado_id):
    """Recuperar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "B":
        abogado.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Recuperado abogado registrado {abogado.nombre}'),
            url=url_for('abogados.detail', abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))
