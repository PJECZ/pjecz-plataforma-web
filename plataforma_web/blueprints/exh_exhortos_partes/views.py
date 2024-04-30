"""
Exh Exhortos Partes, vistas
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
from plataforma_web.blueprints.exh_exhortos_partes.models import ExhExhortoParte

MODULO = "EXH EXHORTOS PARTES"

exh_exhortos_partes = Blueprint("exh_exhortos_partes", __name__, template_folder="templates")


@exh_exhortos_partes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""

@exh_exhortos_partes.route('/exh_exhortos_partes/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Exh Exhortos Partes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhortoParte.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    if 'exh_exhorto_id' in request.form:
        consulta = consulta.filter_by(exh_exhorto_id=request.form['exh_exhorto_id'])
    registros = consulta.order_by(ExhExhortoParte.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        tipo_parte = "NO DEFINIDO"
        if resultado.tipo_parte == 1:
            tipo_parte = "ACTOR"
        elif resultado.tipo_parte == 2:
            tipo_parte = "DEMANDADO"
        else:
            tipo_parte = resultado.tipo_parte_nombre
        data.append(
            {
                'detalle': {
                    'id': resultado.id,
                    'url': url_for('exh_exhortos_partes.detail', exh_exhorto_parte_id=resultado.id),
                },
                'nombre_completo': resultado.nombre_completo,
                'tipo_parte': tipo_parte,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos_partes.route('/exh_exhortos_partes')
def list_active():
    """Listado de Exh Exhortos Partes activos"""
    return render_template(
        'exh_exhortos_partes/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Exhortos Partes',
        estatus='A',
    )


@exh_exhortos_partes.route('/exh_exhortos_partes/<int:exh_exhorto_parte_id>')
def detail(exh_exhorto_parte_id):
    """ Detalle de un Exh Exhorto Parte """
    exh_exhorto_parte = ExhExhortoParte.query.get_or_404(exh_exhorto_parte_id)
    return render_template('exh_exhortos_partes/detail.jinja2', exh_exhorto_parte=exh_exhorto_parte)

