"""
REPSVM Agresores, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_text, safe_url
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor
from plataforma_web.blueprints.repsvm_agresores.forms import REPSVMAgresorForm, REPSVASearchForm

MODULO = "REPSVM AGRESORES"

repsvm_agresores = Blueprint("repsvm_agresores", __name__, template_folder="templates")


@repsvm_agresores.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_agresores.route("/repsvm_agresores/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Agresores"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = REPSVMAgresor.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "distrito_id" in request.form:
        consulta = consulta.filter_by(distrito_id=request.form["distrito_id"])
    if "nombre" in request.form:
        consulta = consulta.filter(REPSVMAgresor.nombre.contains(safe_string(request.form["nombre"])))
    if "numero_causa" in request.form:
        consulta = consulta.filter(REPSVMAgresor.numero_causa.contains(safe_string(request.form["numero_causa"])))
    registros = consulta.order_by(REPSVMAgresor.distrito_id, REPSVMAgresor.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "distrito": {
                    "nombre_corto": resultado.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("repsvm_agresores.detail", repsvm_agresor_id=resultado.id),
                },
                "change_consecutivo": {
                    "id": resultado.id,
                    "consecutivo": resultado.consecutivo,
                },
                "numero_causa": resultado.numero_causa,
                "pena_impuesta": resultado.pena_impuesta,
                "sentencia_url": resultado.sentencia_url,
                "toggle_es_publico": {
                    "id": resultado.id,
                    "consecutivo": resultado.consecutivo,
                    "es_publico": resultado.es_publico,
                    "url": url_for("repsvm_agresores.toggle_es_publico_json", repsvm_agresor_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@repsvm_agresores.route("/repsvm_agresores/toggle_es_publico/<int:repsvm_agresor_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def toggle_es_publico_json(repsvm_agresor_id):
    """Cambiar un agresor para que sea publico o privado"""

    # Consultar agresor
    repsvm_agresor = REPSVMAgresor.query.get(repsvm_agresor_id)
    if repsvm_agresor is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar es_publico a su opuesto
    repsvm_agresor.es_publico = not repsvm_agresor.es_publico

    # Si es publico, definir consecutivo
    if repsvm_agresor.es_publico:
        maximo = REPSVMAgresor.query.filter_by(estatus="A", es_publico=True, distrito_id=repsvm_agresor.distrito_id).order_by(REPSVMAgresor.consecutivo.desc()).first()
        if maximo is None:
            repsvm_agresor.consecutivo = 1  # Es el primero de su distrito
        else:
            repsvm_agresor.consecutivo = maximo.consecutivo + 1  # Es el siguiente de su distrito
    else:
        repsvm_agresor.consecutivo = 0  # No es publico, poner consecutivo en cero

    # Guardar
    repsvm_agresor.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Es publico" if repsvm_agresor.es_publico else "Es privado",
        "consecutivo": repsvm_agresor.consecutivo,
        "es_publico": repsvm_agresor.es_publico,
        "id": repsvm_agresor.id,
    }


@repsvm_agresores.route("/repsvm_agresores")
def list_active():
    """Listado de Agresores activos"""
    return render_template(
        "repsvm_agresores/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="REPSVM Agresores",
        estatus="A",
    )


@repsvm_agresores.route("/repsvm_agresores/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Agresores inactivos"""
    return render_template(
        "repsvm_agresores/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="REPSVM Agresores inactivos",
        estatus="B",
    )


@repsvm_agresores.route("/repsvm_agresores/buscar", methods=["GET", "POST"])
def search():
    """Buscar Agresores"""
    form_search = REPSVASearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data, save_enie=True)
            if nombre != "":
                busqueda["nombre"] = nombre
                titulos.append("nombre " + nombre)
        if form_search.numero_causa.data:
            numero_causa = safe_string(form_search.numero_causa.data)
            if numero_causa != "":
                busqueda["numero_causa"] = numero_causa
                titulos.append("numero_causa " + numero_causa)
        return render_template(
            "repsvm_agresores/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Agresor con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("repsvm_agresores/search.jinja2", form=form_search)


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
        # Definir consecutivo
        distrito = form.distrito.data
        consecutivo = REPSVMAgresor.query.filter_by(estatus="A").filter_by(distrito_id=distrito.id).count() + 1
        # Insertar registro
        repsvm_agresor = REPSVMAgresor(
            distrito=distrito,
            consecutivo=consecutivo,
            delito_generico=safe_string(form.delito_generico.data, save_enie=True),
            delito_especifico=safe_string(form.delito_especifico.data, save_enie=True),
            nombre=safe_string(form.nombre.data, save_enie=True),
            numero_causa=safe_string(form.numero_causa.data, save_enie=True),
            pena_impuesta=safe_string(form.pena_impuesta.data, save_enie=True),
            observaciones=safe_text(form.observaciones.data),
            sentencia_url=safe_url(form.sentencia_url.data),
            tipo_juzgado=safe_string(form.tipo_juzgado.data),
            tipo_sentencia=safe_string(form.tipo_sentencia.data),
        )
        repsvm_agresor.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Agresor {repsvm_agresor.consecutivo} - {repsvm_agresor.nombre}"),
            url=url_for("repsvm_agresores.detail", repsvm_agresor_id=repsvm_agresor.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    if current_user.autoridad.distrito.es_distrito_judicial:
        form.distrito.data = current_user.autoridad.distrito
    return render_template("repsvm_agresores/new.jinja2", form=form)


@repsvm_agresores.route("/repsvm_agresores/edicion/<int:repsvm_agresor_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_agresor_id):
    """Editar Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    form = REPSVMAgresorForm()
    if form.validate_on_submit():
        repsvm_agresor.distrito = form.distrito.data
        repsvm_agresor.delito_generico = safe_string(form.delito_generico.data, save_enie=True)
        repsvm_agresor.delito_especifico = safe_string(form.delito_especifico.data, save_enie=True)
        repsvm_agresor.nombre = safe_string(form.nombre.data, save_enie=True)
        repsvm_agresor.numero_causa = safe_string(form.numero_causa.data, save_enie=True)
        repsvm_agresor.pena_impuesta = safe_string(form.pena_impuesta.data, save_enie=True)
        repsvm_agresor.observaciones = safe_text(form.observaciones.data)
        repsvm_agresor.sentencia_url = safe_url(form.sentencia_url.data)
        repsvm_agresor.tipo_juzgado = safe_string(form.tipo_juzgado.data)
        repsvm_agresor.tipo_sentencia = safe_string(form.tipo_sentencia.data)
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
    form.distrito.data = repsvm_agresor.distrito
    form.delito_generico.data = repsvm_agresor.delito_generico
    form.delito_especifico.data = repsvm_agresor.delito_especifico
    form.nombre.data = repsvm_agresor.nombre
    form.numero_causa.data = repsvm_agresor.numero_causa
    form.pena_impuesta.data = repsvm_agresor.pena_impuesta
    form.observaciones.data = repsvm_agresor.observaciones
    form.sentencia_url.data = repsvm_agresor.sentencia_url
    form.tipo_juzgado.data = repsvm_agresor.tipo_juzgado
    form.tipo_sentencia.data = repsvm_agresor.tipo_sentencia
    return render_template("repsvm_agresores/edit.jinja2", form=form, repsvm_agresor=repsvm_agresor)


@repsvm_agresores.route("/repsvm_agresores/eliminar/<int:repsvm_agresor_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(repsvm_agresor_id):
    """Eliminar Agresor"""
    repsvm_agresor = REPSVMAgresor.query.get_or_404(repsvm_agresor_id)
    if repsvm_agresor.estatus == "A":
        repsvm_agresor.consecutivo = 0  # Poner en cero el consecutivo
        repsvm_agresor.es_publico = False  # Poner en privado
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
        repsvm_agresor.consecutivo = 0  # Poner en cero el consecutivo
        repsvm_agresor.es_publico = False  # Poner en privado
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
