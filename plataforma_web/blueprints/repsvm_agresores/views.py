"""
REPSVM Agresores, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message, safe_text, safe_url
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor
from plataforma_web.blueprints.repsvm_agresores.forms import REPSVMAgresorForm

MODULO = "REPSVM AGRESORES"

repsvm_agresores = Blueprint("repsvm_agresores", __name__, template_folder="templates")


@repsvm_agresores.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_agresores.route("/repsvm_agresores")
def list_active():
    """Listado de Agresores activos"""
    return render_template(
        "repsvm_agresores/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Agresores",
        estatus="A",
    )


@repsvm_agresores.route("/repsvm_agresores/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Agresores inactivos"""
    return render_template(
        "repsvm_agresores/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Agresores inactivos",
        estatus="B",
    )


@repsvm_agresores.route("/repsvm_agresores/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Agresores"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = REPSVMAgresor.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "distrito_id" in request.form:
        consulta = consulta.filter_by(distrito_id=request.form["distrito_id"])
    if "materia_tipo_juzgado_id" in request.form:
        consulta = consulta.filter_by(materia_tipo_juzgado_id=request.form["materia_tipo_juzgado_id"])
    if "repsvm_delito_especifico_id" in request.form:
        consulta = consulta.filter_by(repsvm_delito_especifico_id=request.form["repsvm_delito_especifico_id"])
    if "repsvm_tipo_sentencia_id" in request.form:
        consulta = consulta.filter_by(repsvm_tipo_sentencia_id=request.form["repsvm_tipo_sentencia_id"])
    if "nombre" in request.form:
        consulta = consulta.filter(REPSVMAgresor.nombre.contains(safe_string(request.form["nombre"])))
    registros = consulta.order_by(REPSVMAgresor.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("repsvm_agresores.detail", repsvm_agresor_id=resultado.id),
                },
                "distrito": {
                    "nombre_corto": resultado.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
                "materia_tipo_juzgado": {
                    "clave": resultado.materia_tipo_juzgado.clave,
                    "url": url_for("materias_tipos_juzgados.detail", materia_tipo_juzgado_id=resultado.materia_tipo_juzgado_id) if current_user.can_view("MATERIAS TIPOS JUZGADOS") else "",
                },
                "repsvm_delito_especifico": {
                    "descripcion": resultado.repsvm_delito_especifico.descripcion,
                    "url": url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=resultado.repsvm_delito_especifico_id) if current_user.can_view("REPSVM DELITOS ESPECIFICOS") else "",
                },
                "repsvm_tipo_sentencia": {
                    "nombre": resultado.repsvm_tipo_sentencia.nombre,
                    "url": url_for("repsvm_tipos_sentencias.detail", repsvm_tipo_sentencia_id=resultado.repsvm_tipo_sentencia_id) if current_user.can_view("REPSVM TIPOS SENTENCIAS") else "",
                },
                "nombre": resultado.nombre,
                "numero_causa": resultado.numero_causa,
                "pena_impuesta": resultado.pena_impuesta,
                "sentencia_url": resultado.sentencia_url,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@repsvm_agresores.route("/repsvm_agresores/<int:repsvm_agresor_id>")
def detail(repsvm_agresor_id):
    """Detalle de un Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    return render_template("repsvm_agresores/detail.jinja2", repsvm_agresor=repsvm_agresor)


@repsvm_agresores.route("/repsvm_agresores/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Agresor"""
    form = REPSVMAgresorForm()
    if form.validate_on_submit():
        repsvm_agresor = REPSVMAgresor(
            distrito=form.distrito.data,
            materia_tipo_juzgado=form.materia_tipo_juzgado.data,
            numero_causa=safe_string(form.numero_causa.data),
            nombre=safe_string(form.nombre.data),
            repsvm_delito_especifico=form.repsvm_delito_especifico.data,
            repsvm_tipo_sentencia=form.repsvm_tipo_sentencia.data,
            pena_impuesta=safe_string(form.pena_impuesta.data),
            observaciones=safe_text(form.observaciones.data),
            sentencia_url=safe_url(form.sentencia_url.data),
        )
        repsvm_agresor.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Agresor {repsvm_agresor.nombre}"),
            url=url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("repsvm_agresores/new.jinja2", form=form)


@repsvm_agresores.route("/repsvm_agresores/edicion/<int:repsvm_agresor_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_agresor_id):
    """Editar Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    form = REPSVMAgresorForm()
    if form.validate_on_submit():
        repsvm_agresor.distrito = form.distrito.data
        repsvm_agresor.materia_tipo_juzgado = form.materia_tipo_juzgado.data
        repsvm_agresor.numero_causa = safe_string(form.numero_causa.data)
        repsvm_agresor.nombre = safe_string(form.nombre.data)
        repsvm_agresor.repsvm_delito_especifico = form.repsvm_delito_especifico.data
        repsvm_agresor.repsvm_tipo_sentencia = form.repsvm_tipo_sentencia.data
        repsvm_agresor.pena_impuesta = safe_string(form.pena_impuesta.data)
        repsvm_agresor.observaciones = safe_text(form.observaciones.data)
        repsvm_agresor.sentencia_url = safe_url(form.sentencia_url.data)
        repsvm_agresor.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Agresor {repsvm_agresor.nombre}"),
            url=url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = repsvm_agresor.nombre
    return render_template("repsvm_agresores/edit.jinja2", form=form, repsvm_agresor=repsvm_agresor)


@repsvm_agresores.route("/repsvm_agresores/eliminar/<int:repsvm_agresor_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(repsvm_agresor_id):
    """Eliminar Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    if repsvm_agresor.estatus == "A":
        repsvm_agresor.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Agresor {repsvm_agresor.nombre}"),
            url=url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id))


@repsvm_agresores.route("/repsvm_agresores/recuperar/<int:repsvm_agresor_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(repsvm_agresor_id):
    """Recuperar Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    if repsvm_agresor.estatus == "B":
        repsvm_agresor.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Agresor {repsvm_agresor.nombre}"),
            url=url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id))
