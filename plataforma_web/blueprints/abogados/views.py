"""
Abogados, vistas
"""
import json
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.abogados.models import Abogado
from plataforma_web.blueprints.abogados.forms import AbogadoForm, AbogadoSearchForm
from plataforma_web.blueprints.bitacoras.models import Bitacora

abogados = Blueprint("abogados", __name__, template_folder="templates")

MODULO = "ABOGADOS"


@abogados.before_request
@login_required
@permission_required(Permiso.VER_CONSULTAS)
def before_request():
    """Permiso por defecto"""


@abogados.route("/abogados")
def list_active():
    """Listado de Abogados activos"""
    return render_template(
        "abogados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Abogados registrados",
        estatus="A",
    )


@abogados.route("/abogados/inactivos")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def list_inactive():
    """Listado de Abogados inactivos"""
    return render_template(
        "abogados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Abogados registrados inactivos",
        estatus="B",
    )


@abogados.route("/abogados/buscar", methods=["GET", "POST"])
def search():
    """Buscar Abogados"""
    form_search = AbogadoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("fecha desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("fecha hasta " + busqueda["fecha_hasta"])
        if form_search.numero.data:
            numero = safe_string(form_search.numero.data)
            if numero != "":
                busqueda["numero"] = numero
                titulos.append("número " + numero)
        if form_search.libro.data:
            libro = safe_string(form_search.libro.data)
            if libro != "":
                busqueda["libro"] = libro
                titulos.append("libro " + libro)
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data)
            if nombre != "":
                busqueda["nombre"] = nombre
                titulos.append("nombre " + nombre)
        return render_template(
            "abogados/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Abogados registrados con " + ", ".join(titulos),
        )
    return render_template("abogados/search.jinja2", form=form_search)


@abogados.route("/abogados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de abogados"""
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
    consulta = Abogado.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "fecha_desde" in request.form:
        consulta = consulta.filter(Abogado.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(Abogado.fecha <= request.form["fecha_hasta"])
    if "numero" in request.form:
        consulta = consulta.filter_by(numero=safe_string(request.form["numero"]))
    if "libro" in request.form:
        consulta = consulta.filter_by(libro=safe_string(request.form["libro"]))
    if "nombre" in request.form:
        consulta = consulta.filter(Abogado.nombre.like("%" + safe_string(request.form["nombre"]) + "%"))
    registros = consulta.order_by(Abogado.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for abogado in registros:
        data.append(
            {
                "fecha": abogado.fecha.strftime("%Y-%m-%d"),
                "numero": abogado.numero,
                "libro": abogado.libro,
                "detalle": {
                    "nombre": abogado.nombre,
                    "url": url_for("abogados.detail", abogado_id=abogado.id),
                },
            }
        )
    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@abogados.route("/abogados/<int:abogado_id>")
def detail(abogado_id):
    """Detalle de un Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    return render_template("abogados/detail.jinja2", abogado=abogado)


@abogados.route("/abogados/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CONSULTAS)
def new():
    """Nuevo Abogado"""
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado = Abogado(
            numero=safe_string(form.numero.data),
            nombre=safe_string(form.nombre.data),
            libro=safe_string(form.libro.data),
            fecha=form.fecha.data,
        )
        abogado.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nuevo abogado registrado {abogado.nombre} con número {abogado.numero}"),
            url=url_for("abogados.detail", abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("abogados/new.jinja2", form=form)


@abogados.route("/abogados/edicion/<int:abogado_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def edit(abogado_id):
    """Editar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    form = AbogadoForm()
    if form.validate_on_submit():
        abogado.numero = safe_string(form.numero.data)
        abogado.nombre = safe_string(form.nombre.data)
        abogado.libro = safe_string(form.libro.data)
        abogado.fecha = form.fecha.data
        abogado.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Editado abogado registrado {abogado.nombre}"),
            url=url_for("abogados.detail", abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.numero.data = abogado.numero
    form.nombre.data = abogado.nombre
    form.libro.data = abogado.libro
    form.fecha.data = abogado.fecha
    return render_template("abogados/edit.jinja2", form=form, abogado=abogado)


@abogados.route("/abogados/eliminar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def delete(abogado_id):
    """Eliminar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "A":
        abogado.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Eliminado abogado registrado {abogado.nombre}"),
            url=url_for("abogados.detail", abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))


@abogados.route("/abogados/recuperar/<int:abogado_id>")
@permission_required(Permiso.MODIFICAR_CONSULTAS)
def recover(abogado_id):
    """Recuperar Abogado"""
    abogado = Abogado.query.get_or_404(abogado_id)
    if abogado.estatus == "B":
        abogado.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Recuperado abogado registrado {abogado.nombre}"),
            url=url_for("abogados.detail", abogado_id=abogado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("abogados.detail", abogado_id=abogado_id))
