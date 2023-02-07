"""
Archivo Remesa Documentos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_expediente, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "ARC REMESAS"

arc_remesas_documentos = Blueprint("arc_remesas_documentos", __name__, template_folder="templates")


@arc_remesas_documentos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_remesas_documentos.route("/arc_remesas_documentos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Documentos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcRemesaDocumento.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "remesa_id" in request.form:
        consulta = consulta.filter_by(arc_remesa_id=request.form["remesa_id"])

    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    registros = consulta.order_by(ArcRemesaDocumento.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=resultado.id),
                },
                "expediente": {
                    "expediente": resultado.arc_documento.expediente,
                    "url": url_for("arc_documentos.detail", documento_id=resultado.arc_documento.id),
                },
                "anio": resultado.arc_documento.anio,
                "tipo": resultado.arc_documento.tipo,
                "juicio": resultado.arc_documento.juicio,
                "fojas": {
                    "nuevas": resultado.fojas,
                    "anteriores": resultado.arc_documento.fojas,
                },
                "actor": resultado.arc_documento.actor,
                "demandado": resultado.arc_documento.demandado,
                "partes": {
                    "actor": resultado.arc_documento.actor,
                    "demandado": resultado.arc_documento.demandado,
                },
                "observaciones": resultado.observaciones,
                "ubicacion": resultado.arc_documento.ubicacion,
                "acciones": {
                    "editar": url_for("arc_remesas_documentos.edit", arc_remesa_documento_id=resultado.arc_documento.id),
                    "eliminar": url_for("arc_remesas_documentos.delete", arc_remesa_documento_id=resultado.arc_documento.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_remesas_documentos.route("/arc_remesas_documentos/detalle/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def detail(arc_remesa_documento_id):
    """Detalle de un documento dentro de una Remesa"""
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)
    return render_template("arc_remesas_documentos/detail.jinja2", arc_remesa_documento=remesa_documento)


@arc_remesas_documentos.route("/arc_remesas_documentos/editar/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(arc_remesa_documento_id):
    """Editar un documento dentro de una Remesa"""


@arc_remesas_documentos.route("/arc_remesas_documentos/eliminar/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(arc_remesa_documento_id):
    """Quitar un documento dentro de una Remesa"""
