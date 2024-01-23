"""
Usuarios Nóminas, vistas
"""
import json
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_nominas.models import UsuarioNomina

MODULO = "USUARIOS NOMINAS"

usuarios_nominas = Blueprint("usuarios_nominas", __name__, template_folder="templates")


@usuarios_nominas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_nominas.route("/usuarios_nominas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuario Nómina"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioNomina.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter(UsuarioNomina.usuario_id == current_user.id)
    registros = consulta.order_by(UsuarioNomina.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.fecha_quincena.strftime("%Y-%m-%d"),
                    "descripcion": resultado.descripcion,
                },
                "pdf": {
                    "archivo_pdf": resultado.archivo_pdf,
                    "url_pdf": resultado.url_pdf,
                },
                "xml": {
                    "archivo_xml": resultado.archivo_xml,
                    "url_xml": resultado.url_xml,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_nominas.route("/usuarios_nominas")
def list_active():
    """Listado de Usuarios Nóminas activos"""
    return render_template(
        "usuarios_nominas/list.jinja2",
        filtros=json.dumps({"usuario_id": current_user.id, "estatus": "A"}),
        titulo=f"Recibos de Nómina para {current_user.nombre}",
        estatus="A",
    )
