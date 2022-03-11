"""
Distritos, vistas
"""
import json
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.distritos.forms import DistritoForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "DISTRITOS"

distritos = Blueprint("distritos", __name__, template_folder="templates")


@distritos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@distritos.route("/distritos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Distritos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Distrito.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(Distrito.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("distritos.detail", distrito_id=resultado.id),
                },
                "nombre_corto": resultado.nombre_corto,
                "estatus": resultado.estatus,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@distritos.route("/distritos")
def list_active():
    """Listado de Distritos activos"""
    return render_template(
        "distritos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Distritos",
        estatus="A",
    )


@distritos.route("/distritos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Distritos inactivos"""
    return render_template(
        "distritos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Distritos inactivos",
        estatus="B",
    )


@distritos.route("/distrito/<int:distrito_id>")
def detail(distrito_id):
    """Detalle de un Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template("distritos/detail.jinja2", distrito=distrito)


@distritos.route("/distritos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Distrito"""
    form = DistritoForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if Distrito.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
        else:
            distrito = Distrito(
                nombre=nombre,
                nombre_corto=form.nombre_corto.data.strip(),
                es_distrito_judicial=form.es_distrito_judicial.data,
            )
            distrito.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo distrito {distrito.nombre}"),
                url=url_for("distritos.detail", distrito_id=distrito.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("distritos/new.jinja2", form=form)


@distritos.route("/distritos/edicion/<int:distrito_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(distrito_id):
    """Editar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    form = DistritoForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if distrito.nombre != nombre:
            distrito_existente = Distrito.query.filter_by(nombre=nombre).first()
            if distrito_existente and distrito_existente.id != distrito.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            distrito.nombre = nombre
            distrito.nombre_corto = safe_string(form.nombre_corto.data)
            distrito.es_distrito_judicial = form.es_distrito_judicial.data
            distrito.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado distrito {distrito.nombre}"),
                url=url_for("distritos.detail", distrito_id=distrito.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = distrito.nombre
    form.nombre_corto.data = distrito.nombre_corto
    form.es_distrito_judicial.data = distrito.es_distrito_judicial
    return render_template("distritos/edit.jinja2", form=form, distrito=distrito)


@distritos.route("/distritos/eliminar/<int:distrito_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(distrito_id):
    """Eliminar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "A":
        distrito.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado distrito {distrito.nombre}"),
            url=url_for("distritos.detail", distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("distritos.detail", distrito_id=distrito.id))


@distritos.route("/distritos/recuperar/<int:distrito_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(distrito_id):
    """Recuperar Distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    if distrito.estatus == "B":
        distrito.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado distrito {distrito.nombre}"),
            url=url_for("distritos.detail", distrito_id=distrito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("distritos.detail", distrito_id=distrito.id))
