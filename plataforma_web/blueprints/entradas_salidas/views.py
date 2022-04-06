"""
Entradas-Salidas, vistas
"""
from flask import Blueprint, render_template
from flask.helpers import url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "ENTRADAS SALIDAS"

entradas_salidas = Blueprint("entradas_salidas", __name__, template_folder="templates")


@entradas_salidas.route("/entradas_salidas/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.VER)
def datatable_json():
    """DataTable JSON para listado de entradas y salidas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = EntradaSalida.query
    registros = consulta.order_by(EntradaSalida.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for entrada_salida in registros:
        data.append(
            {
                "creado": entrada_salida.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": entrada_salida.tipo,
                "usuario": {
                    "email": entrada_salida.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=entrada_salida.usuario_id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@entradas_salidas.route("/entradas_salidas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de entradas y salidas"""
    return render_template("entradas_salidas/list.jinja2")
