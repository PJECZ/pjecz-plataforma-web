"""
Distritos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.forms import DistritoForm

distritos = Blueprint("distritos", __name__, template_folder="templates")

MODULO = "DISTRITOS"


@distritos.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """Permiso por defecto"""


@distritos.route("/distritos")
def list_active():
    """Listado de Distritos"""
    distritos_activos = Distrito.query.filter_by(estatus="A").all()
    return render_template("distritos/list.jinja2", distritos=distritos_activos, estatus="A")


@distritos.route("/distritos/inactivos")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def list_inactive():
    """Listado de Distritos inactivos"""
    distritos_inactivos = Distrito.query.filter_by(estatus="B").all()
    return render_template("distritos/list.jinja2", distritos=distritos_inactivos, estatus="B")


@distritos.route("/distritos/<int:distrito_id>")
def detail(distrito_id):
    """Detalle de un Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter_by(estatus="A").all()
    return render_template("distritos/detail.jinja2", distrito=distrito, autoridades=autoridades)


@distritos.route("/distritos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CATALOGOS)
def new():
    """Nuevo Distrito"""
    form = DistritoForm()
    if form.validate_on_submit():
        distrito = Distrito(
            nombre=form.nombre.data.strip(),
            nombre_corto=form.nombre_corto.data.strip(),
            es_distrito_judicial=form.es_distrito_judicial.data,
        )
        distrito.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Distrito {distrito.nombre}"),
            url=url_for("distritos.detail", distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("distritos/new.jinja2", form=form)


@distritos.route("/distritos/edicion/<int:distrito_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def edit(distrito_id):
    """Editar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    form = DistritoForm()
    if form.validate_on_submit():
        distrito.nombre = form.nombre.data.strip()
        distrito.nombre_corto = form.nombre_corto.data.strip()
        distrito.es_distrito_judicial = form.es_distrito_judicial.data
        distrito.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Editado distrito {distrito.nombre}'),
            url=url_for('distritos.detail', distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)
    form.nombre.data = distrito.nombre
    form.nombre_corto.data = distrito.nombre_corto
    form.es_distrito_judicial.data = distrito.es_distrito_judicial
    return render_template("distritos/edit.jinja2", form=form, distrito=distrito)


@distritos.route("/distritos/eliminar/<int:distrito_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(distrito_id):
    """Eliminar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "A":
        distrito.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Eliminado distrito {distrito.nombre}'),
            url=url_for('distritos.detail', distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
    return redirect(url_for("distritos.detail", distrito_id=distrito_id))


@distritos.route("/distritos/recuperar/<int:distrito_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(distrito_id):
    """Recuperar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "B":
        distrito.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f'Recuperado distrito {distrito.nombre}'),
            url=url_for('distritos.detail', distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
    return redirect(url_for("distritos.detail", distrito_id=distrito_id))
