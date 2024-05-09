"""
Permisos, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.forms import PermisoNewWithModuloForm, PermisoNewWithRolForm, PermisoEditForm
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "PERMISOS"

permisos = Blueprint("permisos", __name__, template_folder="templates")


@permisos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@permisos.route("/permisos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Permisos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Permiso.query
    # Solo los modulos en Plataforma Web
    # consulta = consulta.join(Modulo).filter(Modulo.en_plataforma_web == True)
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(Permiso.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Permiso.estatus == "A")
    if "modulo_id" in request.form:
        consulta = consulta.filter(Permiso.modulo_id == request.form["modulo_id"])
    if "rol_id" in request.form:
        consulta = consulta.filter(Permiso.rol_id == request.form["rol_id"])
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Permiso.nombre.contains(nombre))
    if "nivel" in request.form:
        nivel = safe_string(request.form["nivel"], save_enie=True)
        if nivel != "":
            consulta = consulta.filter(Permiso.nivel == nivel)
    # Luego filtrar por columnas de otras tablas
    if "rol_nombre" in request.form:
        rol_nombre = safe_string(request.form["rol_nombre"], save_enie=True)
        if rol_nombre != "":
            consulta = consulta.join(Rol).filter(Rol.nombre.contains(rol_nombre))
    if "modulo_nombre" in request.form:
        modulo_nombre = safe_string(request.form["modulo_nombre"], save_enie=True)
        if modulo_nombre != "":
            consulta = consulta.join(Modulo).filter(Modulo.nombre.contains(modulo_nombre))
    # Ordenar y paginar
    registros = consulta.order_by(Permiso.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("permisos.detail", permiso_id=resultado.id),
                },
                "nivel": resultado.nivel_descrito,
                "modulo": {
                    "nombre": resultado.modulo.nombre,
                    "url": url_for("modulos.detail", modulo_id=resultado.modulo_id) if current_user.can_view("MODULOS") else "",
                },
                "rol": {
                    "nombre": resultado.rol.nombre,
                    "url": url_for("roles.detail", rol_id=resultado.rol_id) if current_user.can_view("ROLES") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@permisos.route("/permisos")
def list_active():
    """Listado de Permisos activos"""
    return render_template(
        "permisos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Permisos",
        estatus="A",
    )


@permisos.route("/permisos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Permisos inactivos"""
    return render_template(
        "permisos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Permisos inactivos",
        estatus="B",
    )


@permisos.route("/permisos/<int:permiso_id>")
def detail(permiso_id):
    """Detalle de un Permiso"""
    permiso = Permiso.query.get_or_404(permiso_id)
    return render_template("permisos/detail.jinja2", permiso=permiso)


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
            flash(f"CONFLICTO: Ya existe {rol.nombre} en {modulo.nombre}. Mejor recupere el registro.", "warning")
            return redirect(url_for("permisos.list_inactive"))
        permiso = Permiso(
            modulo=modulo,
            rol=rol,
            nombre=nombre,
            nivel=nivel,
        )
        permiso.save()
        flash(safe_message(f"Nuevo permiso {nombre}"), "success")
        return redirect(url_for("roles.detail", rol_id=rol.id))
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
        flash(safe_message(f"Nuevo permiso {nombre}"), "success")
        return redirect(url_for("modulos.detail", modulo_id=modulo.id))
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
    return redirect(url_for("permisos.detail", permiso_id=permiso.id))
