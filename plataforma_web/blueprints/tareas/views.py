"""
Tareas, vistas
"""
import json

from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.tareas.models import Tarea

MODULO = "TAREAS"

tareas = Blueprint("tareas", __name__, template_folder="templates")


@tareas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tareas.route('/tareas/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Tareas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Tarea.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    registros = consulta.order_by(Tarea.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                'creado': resultado.creado,
                'nombre': resultado.nombre,
                'descripcion': resultado.descripcion,
                'ha_terminado': resultado.ha_terminado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@tareas.route('/tareas')
def list_active():
    """Listado de Tareas activos"""
    return render_template(
        'tareas/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Tareas',
        estatus='A',
    )


@tareas.route('/tareas/inactivos')
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Tareas inactivos"""
    return render_template(
        'tareas/list.jinja2',
        filtros=json.dumps({'estatus': 'B'}),
        titulo='Tareas inactivos',
        estatus='B',
    )
