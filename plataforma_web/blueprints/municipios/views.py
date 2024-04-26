"""
Municipios, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.municipios.models import Municipio
from plataforma_web.blueprints.estados.models import Estado

MODULO = "MUNICIPIOS"

municipios = Blueprint("municipios", __name__, template_folder="templates")


@municipios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@municipios.route("/municipios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Municipios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Municipio.query
    # Si viene estado_clave o estado_nombre, hacer join con Estado
    if {"estado_clave", "estado_nombre"}.intersection(request.form):
        consulta = consulta.join(Estado)
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "estado_id" in request.form:
        consulta = consulta.filter_by(estado_id=request.form["estado_id"])
    if "municipio_clave" in request.form:
        try:
            municipio_clave = safe_clave(request.form["municipio_clave"], max_len=3).zfill(3)
            if municipio_clave != "":
                consulta = consulta.filter(Municipio.clave.contains(municipio_clave))
        except ValueError:
            pass
    if "municipio_nombre" in request.form:
        municipio_nombre = safe_string(request.form["municipio_nombre"], save_enie=True)
        if municipio_nombre != "":
            consulta = consulta.filter(Municipio.nombre.contains(municipio_nombre))
    if "estado_clave" in request.form:
        try:
            estado_clave = safe_clave(request.form["estado_clave"], max_len=2).zfill(2)
            if estado_clave != "":
                consulta = consulta.filter(Estado.clave.contains(estado_clave))
        except ValueError:
            pass
    if "estado_nombre" in request.form:
        estado_nombre = safe_string(request.form["estado_nombre"], save_enie=True)
        if estado_nombre != "":
            consulta = consulta.filter(Estado.nombre.contains(estado_nombre))
    # Ordenar y paginar
    registros = consulta.order_by(Municipio.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("municipios.detail", municipio_id=resultado.id),
                },
                "municipio_nombre": resultado.nombre,
                "estado_clave": resultado.estado.clave,
                "estado_nombre": resultado.estado.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@municipios.route("/municipios")
def list_active():
    """Listado de Municipios activos"""
    return render_template(
        "municipios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Municipios",
        estatus="A",
    )


@municipios.route("/municipios/<int:municipio_id>")
def detail(municipio_id):
    """Detalle de un Municipio"""
    municipio = Municipio.query.get_or_404(municipio_id)
    return render_template("municipios/detail.jinja2", municipio=municipio)
