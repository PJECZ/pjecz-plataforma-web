"""
Roles, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.roles.forms import RolForm

MODULO = "ROLES"

roles = Blueprint("roles", __name__, template_folder="templates")


@roles.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@roles.route("/roles")
def list_active():
    """Listado de roles"""
    return render_template(
        "roles/list.jinja2",
        roles=Rol.query.filter(Rol.estatus == "A").all(),
        titulo="Roles",
        estatus="A",
    )


@roles.route("/roles/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Roles inactivos"""
    return render_template(
        "roles/list.jinja2",
        roles=Rol.query.filter(Rol.estatus == "B").all(),
        titulo="Roles inactivos",
        estatus="B",
    )


@roles.route("/roles/<int:rol_id>")
def detail(rol_id):
    """Detalle de un rol"""
    rol = Rol.query.get_or_404(rol_id)
    return render_template("roles/detail.jinja2", rol=rol)


@roles.route("/roles/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Rol"""
    form = RolForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if Rol.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
        else:
            rol = Rol(nombre=nombre)
            rol.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo rol {rol.nombre}"),
                url=url_for("roles.detail", rol_id=rol.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("roles/new.jinja2", form=form)


@roles.route("/roles/edicion/<int:rol_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(rol_id):
    """Editar Rol"""
    rol = Rol.query.get_or_404(rol_id)
    form = RolForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if rol.nombre != nombre:
            rol_existente = Rol.query.filter_by(nombre=nombre).first()
            if rol_existente and rol_existente.id != rol.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            rol.nombre = nombre
            rol.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado rol {rol.nombre}"),
                url=url_for("roles.detail", rol_id=rol.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = rol.nombre
    return render_template("roles/edit.jinja2", form=form, rol=rol)


@roles.route("/rol/eliminar/<int:rol_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(rol_id):
    """Eliminar Rol"""
    rol = Rol.query.get_or_404(rol_id)
    if rol.estatus == "A":
        rol.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado rol {rol.nombre}"),
            url=url_for("roles.detail", rol_id=rol.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("rol.detail", rol_id=rol.id))


@roles.route("/roles/recuperar/<int:rol_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(rol_id):
    """Recuperar Rol"""
    rol = Rol.query.get_or_404(rol_id)
    if rol.estatus == "B":
        rol.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado rol {rol.nombre}"),
            url=url_for("roles.detail", rol_id=rol.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("roles.detail", rol_id=rol.id))
