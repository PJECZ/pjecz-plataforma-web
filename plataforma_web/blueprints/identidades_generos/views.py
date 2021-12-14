"""
Identidades Generos, vistas
"""
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_expediente, safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.identidades_generos.models import IdentidadGenero
from plataforma_web.blueprints.identidades_generos.forms import IdentidadGeneroForm

MODULO = "IDENTIDADES GENEROS"

identidades_generos = Blueprint("identidades_generos", __name__, template_folder="templates")


@identidades_generos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@identidades_generos.route("/identidades_generos")
def list_active():
    """Listado de Identidades Géneros activos"""
    return render_template(
        "identidades_generos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Entidades de Géneros",
        estatus="A",
    )


@identidades_generos.route("/identidades_generos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Identidades Géneros inactivos"""
    return render_template(
        "identidades_generos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Entidades de Géneros inactivos",
        estatus="B",
    )


@identidades_generos.route("/identidades_generos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Identidades Géneros"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = IdentidadGenero.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(IdentidadGenero.nombre_actual).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre_actual": resultado.nombre_actual,
                    "url": url_for("identidades_generos.detail", identidad_genero_id=resultado.id),
                },
                "nombre_anterior": resultado.nombre_anterior,
                "fecha_nacimiento": resultado.fecha_nacimiento.strftime("%Y-%m-%d 00:00:00"),
                "lugar_nacimiento": resultado.lugar_nacimiento,
                "genero_anterior": resultado.genero_anterior,
                "genero_actual": resultado.genero_actual,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@identidades_generos.route("/identidades_generos/<int:identidad_genero_id>")
def detail(identidad_genero_id):
    """Detalle de una Identidad de Género"""
    identidad_genero = IdentidadGenero.query.get_or_404(identidad_genero_id)
    return render_template("identidades_generos/detail.jinja2", identidad_genero=identidad_genero)


@identidades_generos.route("/identidades_generos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Identidad de Género"""
    form = IdentidadGeneroForm()
    if form.validate_on_submit():
        identidad_genero = IdentidadGenero(
            nombre_anterior=safe_string(form.nombre_anterior.data),
            nombre_actual=safe_string(form.nombre_actual.data),
            fecha_nacimiento=form.fecha_nacimiento.data,
            lugar_nacimiento=safe_string(form.lugar_nacimiento.data),
            genero_anterior=form.genero_anterior.data,
            genero_actual=form.genero_actual.data,
            nombre_padre=safe_string(form.nombre_padre.data),
            nombre_madre=safe_string(form.nombre_madre.data),
            procedimiento=safe_expediente(form.procedimiento.data),
        )
        identidad_genero.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva identidad de género {identidad_genero.procedimiento}"),
            url=url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("identidades_generos/new.jinja2", form=form)


@identidades_generos.route("/identidades_generos/edicion/<int:identidad_genero_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(identidad_genero_id):
    """Editar Identidad de Género"""
    identidad_genero = IdentidadGenero.query.get_or_404(identidad_genero_id)
    form = IdentidadGeneroForm()
    if form.validate_on_submit():
        identidad_genero.nombre_anterior = safe_string(form.nombre_anterior.data)
        identidad_genero.nombre_actual = safe_string(form.nombre_actual.data)
        identidad_genero.fecha_nacimiento = form.fecha_nacimiento.data
        identidad_genero.lugar_nacimiento = safe_string(form.lugar_nacimiento.data)
        identidad_genero.genero_anterior = form.genero_anterior.data
        identidad_genero.genero_actual = form.genero_actual.data
        identidad_genero.nombre_padre = safe_string(form.nombre_padre.data)
        identidad_genero.nombre_madre = safe_string(form.nombre_madre.data)
        identidad_genero.procedimiento = safe_expediente(form.procedimiento.data)
        identidad_genero.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado identidad de género {identidad_genero.nombre_actual}"),
            url=url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre_anterior.data = identidad_genero.nombre_anterior
    form.nombre_actual.data = identidad_genero.nombre_actual
    form.fecha_nacimiento.data = identidad_genero.fecha_nacimiento
    form.lugar_nacimiento.data = identidad_genero.lugar_nacimiento
    form.genero_anterior.data = identidad_genero.genero_anterior
    form.genero_actual.data = identidad_genero.genero_actual
    form.nombre_padre.data = identidad_genero.nombre_padre
    form.nombre_madre.data = identidad_genero.nombre_madre
    form.procedimiento.data = identidad_genero.procedimiento
    return render_template("identidades_generos/edit.jinja2", form=form, identidad_genero=identidad_genero)


@identidades_generos.route("/identidades_generos/eliminar/<int:identidad_genero_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(identidad_genero_id):
    """Eliminar Identidad de Género"""
    identidad_genero = IdentidadGenero.query.get_or_404(identidad_genero_id)
    if identidad_genero.estatus == "A":
        identidad_genero.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado identidad de género {identidad_genero.nombre_actual}"),
            url=url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id))


@identidades_generos.route("/identidades_generos/recuperar/<int:identidad_genero_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(identidad_genero_id):
    """Recuperar Identidad de Género"""
    identidad_genero = IdentidadGenero.query.get_or_404(identidad_genero_id)
    if identidad_genero.estatus == "B":
        identidad_genero.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado identidad de género {identidad_genero.nombre_actual}"),
            url=url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("identidades_generos.detail", identidad_genero_id=identidad_genero.id))
