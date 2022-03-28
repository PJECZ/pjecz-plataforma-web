"""
Modulos, vistas
"""
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.modulos.forms import ModuloForm
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "MODULOS"

modulos = Blueprint("modulos", __name__, template_folder="templates")


@modulos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@modulos.route("/modulos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Modulos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Modulo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(Modulo.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("modulos.detail", modulo_id=resultado.id),
                },
                "icono": resultado.icono,
                "en_navegacion": resultado.en_navegacion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@modulos.route("/modulos")
def list_active():
    """Listado de Modulos activos"""
    return render_template(
        "modulos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Módulos",
        estatus="A",
    )


@modulos.route("/modulos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Modulos inactivos"""
    return render_template(
        "modulos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Módulos inactivos",
        estatus="B",
    )


@modulos.route("/modulos/<int:modulo_id>")
def detail(modulo_id):
    """Detalle de un Modulo"""
    modulo = Modulo.query.get_or_404(modulo_id)
    return render_template("modulos/detail.jinja2", modulo=modulo)


@modulos.route("/modulos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Modulo"""
    form = ModuloForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if Modulo.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
        else:
            modulo = Modulo(
                nombre=nombre,
                nombre_corto=form.nombre_corto.data,
                icono=form.icono.data,
                ruta=form.ruta.data,
                en_navegacion=form.en_navegacion.data == 1,
            )
            modulo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo módulo {modulo.nombre}"),
                url=url_for("modulos.detail", modulo_id=modulo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("modulos/new.jinja2", form=form)


@modulos.route("/modulos/edicion/<int:modulo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(modulo_id):
    """Editar Modulo"""
    modulo = Modulo.query.get_or_404(modulo_id)
    form = ModuloForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if modulo.nombre != nombre:
            modulo_existente = Modulo.query.filter_by(nombre=nombre).first()
            if modulo_existente and modulo_existente.id != modulo.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            modulo.nombre = nombre
            modulo.nombre_corto = safe_string(form.nombre_corto.data)
            modulo.icono = form.icono.data
            modulo.ruta = form.ruta.data
            modulo.en_navegacion = form.en_navegacion.data == 1
            modulo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado módulo {modulo.nombre}"),
                url=url_for("modulos.detail", modulo_id=modulo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = modulo.nombre
    form.nombre_corto.data = modulo.nombre_corto
    form.icono.data = modulo.icono
    form.ruta.data = modulo.ruta
    if modulo.en_navegacion:
        form.en_navegacion.data = 1
    else:
        form.en_navegacion.data = 0
    return render_template("modulos/edit.jinja2", form=form, modulo=modulo)


@modulos.route("/modulos/eliminar/<int:modulo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(modulo_id):
    """Eliminar Modulo"""
    modulo = Modulo.query.get_or_404(modulo_id)
    if modulo.estatus == "A":
        modulo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado módulo {modulo.nombre}"),
            url=url_for("modulos.detail", modulo_id=modulo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("modulos.detail", modulo_id=modulo.id))


@modulos.route("/modulos/recuperar/<int:modulo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(modulo_id):
    """Recuperar Modulo"""
    modulo = Modulo.query.get_or_404(modulo_id)
    if modulo.estatus == "B":
        modulo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado módulo {modulo.nombre}"),
            url=url_for("modulos.detail", modulo_id=modulo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("modulos.detail", modulo_id=modulo.id))
