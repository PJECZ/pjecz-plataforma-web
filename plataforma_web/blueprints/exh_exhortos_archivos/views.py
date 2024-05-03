"""
Exh Exhortos Archivos, vistas
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
from plataforma_web.blueprints.exh_exhortos_archivos.models import ExhExhortoArchivo

MODULO = "EXH EXHORTOS ARCHIVOS"

exh_exhortos_archivos = Blueprint("exh_exhortos_archivos", __name__, template_folder="templates")


@exh_exhortos_archivos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""

@exh_exhortos_archivos.route('/exh_exhortos_archivos/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Exh Exhortos Archivos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhortoArchivo.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    if 'exh_exhorto_id' in request.form:
        consulta = consulta.filter_by(exh_exhorto_id=request.form['exh_exhorto_id'])
    registros = consulta.order_by(ExhExhortoArchivo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        # Dar descripción al tipo de documento
        tipo_documento = "NO DEFINIDO"
        if resultado.tipo_documento == 1:
            tipo_documento = "OFICIO"
        elif resultado.tipo_documento == 2:
            tipo_documento = "ACUERDO"
        elif resultado.tipo_documento == 3:
            tipo_documento = "ANEXO"
        # Apilar resultados
        data.append(
            {
                'nombre_archivo': resultado.nombre_archivo,
                'tipo_documento': tipo_documento,
                'url': resultado.url,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos_archivos.route('/exh_exhortos_archivos')
def list_active():
    """Listado de Exh Exhortos Archivos activos"""
    return render_template(
        'exh_exhortos_archivos/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Exhortos Archivos',
        estatus='A',
    )
