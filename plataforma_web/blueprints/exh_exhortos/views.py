"""
Exh Exhortos, vistas
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
from plataforma_web.blueprints.exh_exhortos.models import ExhExhorto

MODULO = "EXH EXHORTOS"

exh_exhortos = Blueprint("exh_exhortos", __name__, template_folder="templates")


@exh_exhortos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_exhortos.route('/exh_exhortos/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Exh Exhortos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhorto.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    registros = consulta.order_by(ExhExhorto.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                'detalle': {
                    'nombre': resultado.id,
                    'url': url_for('exh_exhortos.detail', exh_exhorto_id=resultado.id),
                },
                'UUID': resultado.exhorto_origen_id,
                'juzgado_origen': resultado.juzgado_origen_id,
                'juzgado_nombre': resultado.juzgado_origen_nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos.route('/exh_exhortos')
def list_active():
    """Listado de Exh Exhortos activos"""
    return render_template(
        'exh_exhortos/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Exhortos',
        estatus='A',
    )


@exh_exhortos.route('/exh_exhortos/<int:exh_exhorto_id>')
def detail(exh_exhorto_id):
    """ Detalle de un Exh Exhorto """
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    return render_template('exh_exhortos/detail.jinja2', exh_exhorto=exh_exhorto)

