"""
Permisos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.permisos.forms import PermisoNewForm, PermisoNewWithModuloForm, PermisoNewWithRolForm, PermisoEditForm
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "PERMISOS"

permisos = Blueprint("permisos", __name__, template_folder="templates")


@permisos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@permisos.route("/permisos")
def list_active():
    """Listado de Permisos activos"""
    return render_template(
        "permisos/list.jinja2",
        permisos=Permiso.query.filter_by(estatus="A").all(),
        titulo="Permisos",
        estatus="A",
    )


@permisos.route("/permisos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Permisos inactivos"""
    return render_template(
        "permisos/list.jinja2",
        permisos=Permiso.query.filter_by(estatus="B").all(),
        titulo="Permisos inactivos",
        estatus="B",
    )


@permisos.route("/permisos/<int:permiso_id>")
def detail(permiso_id):
    """Detalle de un Permiso"""
    permiso = Permiso.query.get_or_404(permiso_id)
    return render_template("permisos/detail.jinja2", permiso=permiso)


@permisos.route("/permisos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Permiso"""
    form = PermisoNewForm()
    if form.validate_on_submit():
        modulo = form.modulo.data
        rol = form.rol.data
        nivel = form.nivel.data
        nombre = f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}"
        if Permiso.query.filter(Permiso.modulo == modulo).filter(Permiso.rol == rol).first() is not None:
            flash(f"CONFLICTO: Ya existe {nombre}. Mejor recupere el registro.", "warning")
            return redirect(url_for("permisos.list_inactive"))
        permiso = Permiso(
            modulo=modulo,
            rol=rol,
            nombre=nombre,
            nivel=nivel,
        )
        permiso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo permiso {nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("permisos/new.jinja2", form=form, titulo="Nuevo Permiso")


@permisos.route("/permisos/nuevo_con_rol/<int:rol_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_rol(rol_id):
    """Nuevo Permiso con Rol"""
    rol = Rol.query.get_or_404(rol_id)
    form = PermisoNewWithRolForm()
    if form.validate_on_submit():
        modulo = form.modulo.data
        nivel = form.nivel.data
        nombre = f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}"
        if Permiso.query.filter(Permiso.modulo == modulo).filter(Permiso.rol == rol).first() is not None:
            flash(f"CONFLICTO: Ya existe {nombre}. Mejor recupere el registro.", "warning")
            return redirect(url_for("permisos.list_inactive"))
        permiso = Permiso(
            modulo=modulo,
            rol=rol,
            nombre=nombre,
            nivel=nivel,
        )
        permiso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo permiso {nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.rol.data = rol.nombre
    return render_template(
        "permisos/new_with_rol.jinja2",
        form=form,
        rol=rol,
        titulo=f"Agregar permiso al rol {rol.nombre}",
    )


@permisos.route("/permisos/nuevo_con_modulo/<int:modulo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_modulo(modulo_id):
    """Nuevo Permiso con Modulo"""
    modulo = Modulo.query.get_or_404(modulo_id)
    form = PermisoNewWithModuloForm()
    if form.validate_on_submit():
        rol = form.rol.data
        nivel = form.nivel.data
        nombre = f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}"
        if Permiso.query.filter(Permiso.modulo == modulo).filter(Permiso.rol == rol).first() is not None:
            flash(f"CONFLICTO: Ya existe {nombre}. Mejor recupere el registro.", "warning")
            return redirect(url_for("permisos.list_inactive"))
        permiso = Permiso(
            modulo=modulo,
            rol=rol,
            nombre=nombre,
            nivel=nivel,
        )
        permiso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo permiso {nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.modulo.data = modulo.nombre
    return render_template(
        "permisos/new_with_modulo.jinja2",
        form=form,
        modulo=modulo,
        titulo=f"Agregar permiso al módulo {modulo.nombre}",
    )


@permisos.route("/permisos/edicion/<int:permiso_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(permiso_id):
    """Editar Permiso"""
    permiso = Permiso.query.get_or_404(permiso_id)
    form = PermisoEditForm()
    if form.validate_on_submit():
        permiso.nivel = form.nivel.data
        permiso.nombre = f"{permiso.rol.nombre} puede {Permiso.NIVELES[permiso.nivel]} en {permiso.modulo.nombre}"
        permiso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado permiso {permiso.nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nivel.data = permiso.nivel
    return render_template("permisos/edit.jinja2", form=form, permiso=permiso)


@permisos.route("/permisos/eliminar/<int:permiso_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(permiso_id):
    """Eliminar Permiso"""
    permiso = Permiso.query.get_or_404(permiso_id)
    if permiso.estatus == "A":
        permiso.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado permiso {permiso.nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("permisos.detail", permiso_id=permiso.id))


@permisos.route("/permisos/recuperar/<int:permiso_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(permiso_id):
    """Recuperar Permiso"""
    permiso = Permiso.query.get_or_404(permiso_id)
    if permiso.estatus == "B":
        permiso.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado permiso {permiso.nombre}"),
            url=url_for("permisos.detail", permiso_id=permiso.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
        # flash(f"Permiso {permiso.nombre} recuperado.", "success")
    return redirect(url_for("permisos.detail", permiso_id=permiso.id))
