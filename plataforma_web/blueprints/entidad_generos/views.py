"""
Entidad Generos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.entidad_generos.models import EntidadGenero

from .forms import EntidadGeneroForm

MODULO = "ENTIDAD GENEROS"

entidad_generos = Blueprint("entidad_generos", __name__, template_folder="templates")


@entidad_generos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@entidad_generos.route("/entidad_generos")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Entidad de Géneros activos"""
    activos = EntidadGenero.query.filter(EntidadGenero.estatus == "A").all()
    return render_template("entidad_generos/list.jinja2", registros=activos, titulo="Entidad de Géneros", estatus="A")


@entidad_generos.route("/entidad_generos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Entidad de Género inactivos"""
    inactivos = EntidadGenero.query.filter(EntidadGenero.estatus == "B").all()
    return render_template(
        "entidad_generos/list.jinja2",
        registros=inactivos,
        titulo="Entidad de Género inactivos",
        estatus="B",
    )


@entidad_generos.route("/entidad_generos/<int:entidad_genero_id>")
def detail(entidad_genero_id):
    """Detalle de un Entidad de Género"""
    registro = EntidadGenero.query.get_or_404(entidad_genero_id)
    return render_template("entidad_generos/detail.jinja2", entidad_genero=registro)


@entidad_generos.route("/entidad_generos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Entidad de Género"""
    form = EntidadGeneroForm()
    if form.validate_on_submit():
        entidad_genero = EntidadGenero(
            nombre_anterior=form.nombre_anterior.data,
            nombre_actual=form.nombre_actual.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            lugar_nacimiento=form.lugar_nacimiento.data,
            genero_anterior=form.genero_anterior.data,
            genero_actual=form.genero_actual.data,
            nombre_padre=form.nombre_padre.data,
            nombre_madre=form.nombre_madre.data,
            procedimiento=form.procedimiento.data,
        )
        entidad_genero.save()

        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva entidad de genero {entidad_genero.procedimiento}"),
            url=url_for("entidad_generos.detail", entidad_genero_id=entidad_genero.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("entidad_generos/new.jinja2", form=form)


@entidad_generos.route("/entidad_generos/edicion/<int:entidad_genero_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(entidad_genero_id):
    """Editar Entidad de Género"""
    entidad_genero = EntidadGenero.query.get_or_404(entidad_genero_id)
    form = EntidadGeneroForm()
    if form.validate_on_submit():
        entidad_genero.nombre_anterior = form.nombre_anterior.data
        entidad_genero.nombre_actual = form.nombre_actual.data
        entidad_genero.fecha_nacimiento = form.fecha_nacimiento.data
        entidad_genero.lugar_nacimiento = form.lugar_nacimiento.data
        entidad_genero.genero_anterior = form.genero_anterior.data
        entidad_genero.genero_actual = form.genero_actual.data
        entidad_genero.nombre_padre = form.nombre_padre.data
        entidad_genero.nombre_madre = form.nombre_madre.data
        entidad_genero.procedimiento = form.procedimiento.data
        entidad_genero.save()
        flash(f"Entidad de Género {entidad_genero.nombre_anterior} guardado.", "success")
        return redirect(url_for("entidad_generos.detail", entidad_genero_id=entidad_genero.id))
    form.nombre_anterior.data = entidad_genero.nombre_anterior
    form.nombre_actual.data = entidad_genero.nombre_actual
    form.fecha_nacimiento.data = entidad_genero.fecha_nacimiento
    form.lugar_nacimiento.data = entidad_genero.lugar_nacimiento
    form.genero_anterior.data = entidad_genero.genero_anterior
    form.genero_actual.data = entidad_genero.genero_actual
    form.nombre_padre.data = entidad_genero.nombre_padre
    form.nombre_madre.data = entidad_genero.nombre_madre
    form.procedimiento.data = entidad_genero.procedimiento
    return render_template("entidad_generos/edit.jinja2", form=form, entidad_genero=entidad_genero)


@entidad_generos.route("/entidad_generos/eliminar/<int:entidad_genero_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(entidad_genero_id):
    """Eliminar Entidad de Género"""
    entidad_genero = EntidadGenero.query.get_or_404(entidad_genero_id)
    if entidad_genero.estatus == "A":
        entidad_genero.delete()
        flash(f"Entidad de Género {entidad_genero.nombre_anterior} eliminado.", "success")
    return redirect(url_for("entidad_generos.detail", entidad_genero_id=entidad_genero.id))


@entidad_generos.route("/entidad_generos/recuperar/<int:entidad_genero_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(entidad_genero_id):
    """Recuperar Entidad de Género"""
    entidad_genero = EntidadGenero.query.get_or_404(entidad_genero_id)
    if entidad_genero.estatus == "B":
        entidad_genero.recover()
        flash(f"Entidad de Género {entidad_genero.nombre_anterior} recuperado.", "success")
    return redirect(url_for("entidad_generos.detail", entidad_genero_id=entidad_genero.id))
