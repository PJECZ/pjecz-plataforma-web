"""
Soporte Categorias, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.soportes_categorias.forms import SoporteCategoriaForm

MODULO = "SOPORTES CATEGORIAS"

soportes_categorias = Blueprint("soportes_categorias", __name__, template_folder="templates")


@soportes_categorias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_categorias.route("/soportes_categorias")
def list_active():
    """Listado de Soportes Categorias activas"""
    soportes_categorias_activas = SoporteCategoria.query.filter(SoporteCategoria.estatus == "A").all()
    return render_template(
        "soportes_categorias/list.jinja2",
        soportes_categorias=soportes_categorias_activas,
        titulo="Soportes Categorias",
        estatus="A",
    )


@soportes_categorias.route("/soportes_categorias/inactivas")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Soportes Categorias inactivas"""
    soportes_categorias_inactivas = SoporteCategoria.query.filter(SoporteCategoria.estatus == "B").all()
    return render_template(
        "soportes_categorias/list.jinja2",
        soportes_categorias=soportes_categorias_inactivas,
        titulo="Soportes Categorias inactivas",
        estatus="B",
    )


@soportes_categorias.route("/soportes_categorias/<int:soporte_categoria_id>")
def detail(soporte_categoria_id):
    """Detalle de un Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    return render_template("soportes_categorias/detail.jinja2", soporte_categoria=soporte_categoria)


@soportes_categorias.route("/soportes_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Soporte Categoria"""
    form = SoporteCategoriaForm()
    if form.validate_on_submit():
        soporte_categoria = SoporteCategoria(nombre=safe_string(form.nombre.data))
        soporte_categoria.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo soporte categoria {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("soportes_categorias/new.jinja2", form=form)


@soportes_categorias.route("/soportes_categorias/edicion/<int:soporte_categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(soporte_categoria_id):
    """Editar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    form = SoporteCategoriaForm()
    if form.validate_on_submit():
        soporte_categoria.nombre = safe_string(form.nombre.data)
        soporte_categoria.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado soporte categoria {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = soporte_categoria.nombre
    return render_template("soportes_categorias/edit.jinja2", form=form, soporte_categoria=soporte_categoria)


@soportes_categorias.route("/soportes_categorias/eliminar/<int:soporte_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(soporte_categoria_id):
    """Eliminar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    if soporte_categoria.estatus == "A":
        soporte_categoria.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado soporte_categoria_id {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id))


@soportes_categorias.route("/soportes_categorias/recuperar/<int:soporte_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(soporte_categoria_id):
    """Recuperar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    if soporte_categoria.estatus == "B":
        soporte_categoria.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado soporte_categoria_id {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id))
