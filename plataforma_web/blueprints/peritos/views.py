"""
Peritos, vistas
"""
import json
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.peritos.forms import PeritoForm, PeritoSearchForm

peritos = Blueprint("peritos", __name__, template_folder="templates")

MODULO = "PERITOS"


@peritos.before_request
@login_required
@permission_required(Permiso.VER_CONSULTAS)
def before_request():
    """Permiso por defecto"""


@peritos.route("/peritos")
def list_active():
    """Listado de Peritos"""
    return render_template(
        "peritos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Peritos",
        estatus="A",
    )


@peritos.route("/peritos/inactivos")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def list_inactive():
    """Listado de Peritos inactivos"""
    return render_template(
        "peritos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Peritos inactivos",
        estatus="B",
    )


@peritos.route("/peritos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Peritos"""
    form_search = PeritoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.distrito.data:
            distrito = form_search.distrito.data
            busqueda["distrito_id"] = distrito.id
            titulos.append(distrito.nombre)
        if form_search.nombre.data:
            busqueda["nombre"] = safe_string(form_search.nombre.data)
            titulos.append("nombre " + busqueda["nombre"])
        if form_search.tipo.data:
            busqueda["tipo"] = safe_string(form_search.tipo.data)
            titulos.append("tipo " + busqueda["tipo"])
        return render_template(
            "peritos/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Peritos con " + ", ".join(titulos),
        )
    return render_template("peritos/search.jinja2", form=form_search)


@peritos.route("/peritos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de peritos"""
    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10
    # Consultar
    consulta = Perito.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "distrito_id" in request.form:
        distrito = Distrito.query.get(request.form["distrito_id"])
        if distrito:
            consulta = consulta.filter(Perito.distrito == distrito)
    if "nombre" in request.form:
        consulta = consulta.filter(Perito.nombre.like("%" + safe_string(request.form["nombre"]) + "%"))
    if "tipo" in request.form:
        consulta = consulta.filter_by(tipo=safe_string(request.form["tipo"]))
    registros = consulta.order_by(Perito.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for perito in registros:
        data.append(
            {
                "detalle": {
                    "nombre": perito.nombre,
                    "url": url_for("peritos.detail", perito_id=perito.id),
                },
                "tipo": perito.tipo,
                "departamento": perito.distrito.nombre,
            }
        )
    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@peritos.route("/peritos/<int:perito_id>")
def detail(perito_id):
    """Detalle de un Perito"""
    perito = Perito.query.get_or_404(perito_id)
    return render_template("peritos/detail.jinja2", perito=perito)


@peritos.route("/peritos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONSULTAS)
def new():
    """Nuevo Perito"""
    form = PeritoForm()
    if form.validate_on_submit():
        perito = Perito(
            distrito=form.distrito.data,
            tipo=form.tipo.data,
            nombre=safe_string(form.nombre.data),
            domicilio=safe_string(form.domicilio.data),
            telefono_fijo=safe_string(form.telefono_fijo.data),
            telefono_celular=safe_string(form.telefono_celular.data),
            email=form.email.data,
            renovacion=form.renovacion.data,
            notas=safe_string(form.notas.data),
        )
        perito.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nuevo perito {perito.nombre}, tipo {perito.tipo} en {perito.distrito.nombre}"),
            url=url_for("peritos.detail", perito_id=perito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("peritos/new.jinja2", form=form)


@peritos.route("/peritos/edicion/<int:perito_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def edit(perito_id):
    """Editar Perito"""
    perito = Perito.query.get_or_404(perito_id)
    form = PeritoForm()
    if form.validate_on_submit():
        perito.distrito = form.distrito.data
        perito.tipo = form.tipo.data
        perito.nombre = safe_string(form.nombre.data)
        perito.domicilio = safe_string(form.domicilio.data)
        perito.telefono_fijo = safe_string(form.telefono_fijo.data)
        perito.telefono_celular = safe_string(form.telefono_celular.data)
        perito.email = form.email.data
        perito.renovacion = form.renovacion.data
        perito.notas = safe_string(form.notas.data)
        perito.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Editado perito {perito.nombre} de {perito.distrito.nombre}"),
            url=url_for("peritos.detail", perito_id=perito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = perito.distrito
    form.tipo.data = perito.tipo
    form.nombre.data = perito.nombre
    form.domicilio.data = perito.domicilio
    form.telefono_fijo.data = perito.telefono_fijo
    form.telefono_celular.data = perito.telefono_celular
    form.email.data = perito.email
    form.renovacion.data = perito.renovacion
    form.notas.data = perito.notas
    return render_template("peritos/edit.jinja2", form=form, perito=perito)


@peritos.route("/peritos/eliminar/<int:perito_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def delete(perito_id):
    """Eliminar Perito"""
    perito = Perito.query.get_or_404(perito_id)
    if perito.estatus == "A":
        perito.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Eliminado perito {perito.nombre} de {perito.distrito.nombre}"),
            url=url_for("peritos.detail", perito_id=perito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("peritos.detail", perito_id=perito_id))


@peritos.route("/peritos/recuperar/<int:perito_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def recover(perito_id):
    """Recuperar Perito"""
    perito = Perito.query.get_or_404(perito_id)
    if perito.estatus == "B":
        perito.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Recuperado perito {perito.nombre} de {perito.distrito.nombre}"),
            url=url_for("peritos.detail", perito_id=perito.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("peritos.detail", perito_id=perito_id))
