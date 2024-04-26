"""
Estados, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.estados.models import Estado

MODULO = "ESTADOS"

estados = Blueprint("estados", __name__, template_folder="templates")


@estados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@estados.route("/estados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Estados"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Estado.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"], max_len=2).zfill(2)
            if clave != "":
                consulta = consulta.filter(Estado.clave.contains(clave))
        except ValueError:
            pass
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Estado.nombre.contains(nombre))
    # Ordenar y paginar
    registros = consulta.order_by(Estado.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("estados.detail", estado_id=resultado.id),
                },
                "nombre": resultado.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@estados.route("/estados")
def list_active():
    """Listado de Estados activos"""
    return render_template(
        "estados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Estados",
        estatus="A",
    )


@estados.route("/estados/<int:estado_id>")
def detail(estado_id):
    """Detalle de un Estado"""
    estado = Estado.query.get_or_404(estado_id)
    return render_template("estados/detail.jinja2", estado=estado)
