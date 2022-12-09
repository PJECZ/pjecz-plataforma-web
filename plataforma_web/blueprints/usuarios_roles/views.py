"""
Usuarios Roles, vistas
"""
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol
from plataforma_web.blueprints.usuarios_roles.forms import UsuarioRolWithUsuarioForm

MODULO = "USUARIOS ROLES"

usuarios_roles = Blueprint("usuarios_roles", __name__, template_folder="templates")


@usuarios_roles.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_roles.route("/usuarios_roles/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuarios Roles"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioRol.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    if "rol_id" in request.form:
        consulta = consulta.filter_by(rol_id=request.form["rol_id"])
    registros = consulta.order_by(UsuarioRol.descripcion).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("usuarios_roles.detail", usuario_rol_id=resultado.id),
                },
                "usuario": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "usuario_nombre": resultado.usuario.nombre,
                "usuario_puesto": resultado.usuario.puesto,
                "rol": {
                    "nombre": resultado.rol.nombre,
                    "url": url_for("roles.detail", rol_id=resultado.rol_id) if current_user.can_view("ROLES") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_roles.route("/usuarios_roles/datatable_toggle_estatus_json", methods=["GET", "POST"])
def datatable_toggle_estatus_json():
    """DataTable JSON que entrega los roles de un usuario donde se muestra el boton para activar o desactivar"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioRol.query
    if "rol_id" in request.form:
        consulta = consulta.filter_by(rol_id=request.form["rol_id"])
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    registros = consulta.order_by(UsuarioRol.descripcion).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("usuarios_roles.detail", usuario_rol_id=resultado.id),
                },
                "usuario": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "usuario_nombre": resultado.usuario.nombre,
                "usuario_puesto": resultado.usuario.puesto,
                "rol": {
                    "nombre": resultado.rol.nombre,
                    "url": url_for("roles.detail", rol_id=resultado.rol_id) if current_user.can_view("ROLES") else "",
                },
                "toggle_estatus": {
                    "id": resultado.id,
                    "estatus": resultado.estatus,
                    "url": url_for("usuarios_roles.toggle_estatus_json", usuario_rol_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_roles.route("/usuarios_roles/toggle_estatus_json/<int:usuario_rol_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def toggle_estatus_json(usuario_rol_id):
    """Cambiar el estatus de un usuario-rol"""

    # Consultar usuario-rol
    usuario_rol = UsuarioRol.query.get_or_404(usuario_rol_id)
    if usuario_rol is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar estatus a su opuesto
    if usuario_rol.estatus == "A":
        usuario_rol.estatus = "B"
    else:
        usuario_rol.estatus = "A"

    # Guardar
    usuario_rol.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Activo" if usuario_rol.estatus == "A" else "Inactivo",
        "estatus": usuario_rol.estatus,
        "id": usuario_rol.id,
    }


@usuarios_roles.route("/usuarios_roles")
def list_active():
    """Listado de Usuarios Roles activos"""
    return render_template(
        "usuarios_roles/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios Roles",
        estatus="A",
    )


@usuarios_roles.route("/usuarios_roles/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Usuarios Roles inactivos"""
    return render_template(
        "usuarios_roles/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios Roles inactivos",
        estatus="B",
    )


@usuarios_roles.route("/usuarios_roles/usuario/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def list_usuario(usuario_id):
    """Listado de los roles de un usuario donde se muestra el boton para activar o desactivar"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template(
        "usuarios_roles/list_usuario.jinja2",
        filtros=json.dumps({"usuario_id": usuario_id}),
        titulo=f"Roles de {usuario.email}",
        usuario=usuario,
    )


@usuarios_roles.route("/usuarios_roles/<int:usuario_rol_id>")
def detail(usuario_rol_id):
    """Detalle de un Usuario Rol"""
    usuario_rol = UsuarioRol.query.get_or_404(usuario_rol_id)
    return render_template("usuarios_roles/detail.jinja2", usuario_rol=usuario_rol)


@usuarios_roles.route("/usuarios_roles/nuevo_con_usuario/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_usuario(usuario_id):
    """Nuevo Usuario-Rol con Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioRolWithUsuarioForm()
    if form.validate_on_submit():
        rol = form.rol.data
        descripcion = f"{usuario.email} en {rol.nombre}"
        if UsuarioRol.query.filter(UsuarioRol.rol == rol).filter(UsuarioRol.usuario == usuario).first() is not None:
            flash(f"CONFLICTO: Ya existe {descripcion}. Mejor recupere el registro.", "warning")
            return redirect(url_for("usuarios_roles.list_inactive"))
        usuario_rol = UsuarioRol(
            rol=rol,
            usuario=usuario,
            descripcion=descripcion,
        )
        usuario_rol.save()
        flash(safe_message(f"Nuevo {descripcion}"), "success")
        return redirect(url_for("usuarios.detail", usuario_id=usuario.id))
    form.usuario.data = usuario.email
    return render_template(
        "usuarios_roles/new_with_usuario.jinja2",
        form=form,
        usuario=usuario,
        titulo=f"Agregar rol al usuario {usuario.email}",
    )


@usuarios_roles.route("/usuarios_roles/eliminar/<int:usuario_rol_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(usuario_rol_id):
    """Eliminar Usuario-Rol"""
    usuario_rol = UsuarioRol.query.get_or_404(usuario_rol_id)
    if usuario_rol.estatus == "A":
        usuario_rol.delete()
        flash(safe_message(f"Eliminado usuario-rol {usuario_rol.descripcion}"), "success")
        return redirect(url_for("usuarios_roles.detail", usuario_rol_id=usuario_rol.id))
    return redirect(url_for("usuarios_roles.detail", usuario_rol_id=usuario_rol.id))


@usuarios_roles.route("/usuarios_roles/recuperar/<int:usuario_rol_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(usuario_rol_id):
    """Recuperar Usuario-Rol"""
    usuario_rol = UsuarioRol.query.get_or_404(usuario_rol_id)
    if usuario_rol.estatus == "B":
        usuario_rol.recover()
        flash(safe_message(f"Recuperado usuario-rol {usuario_rol.descripcion}"), "success")
        return redirect(url_for("usuarios_roles.detail", usuario_rol_id=usuario_rol.id))
    return redirect(url_for("usuarios_roles.detail", usuario_rol_id=usuario_rol.id))
