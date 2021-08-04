"""
Entradas-Salidas, vistas
"""
from flask import Blueprint, request, render_template
from flask.helpers import url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida

entradas_salidas = Blueprint("entradas_salidas", __name__, template_folder="templates")


@entradas_salidas.route("/entradas_salidas")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def list_active():
    """Listado de entradas y salidas"""
    return render_template("entradas_salidas/list.jinja2")


@entradas_salidas.route("/entradas_salidas/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(Permiso.VER_CUENTAS)
def json():
    """DataTable JSON para listado de entradas y salidas"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])  # Número de Página
        start = int(request.form["start"])  # Registro inicial
        rows_per_page = int(request.form["length"])  # Renglones por página
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    consulta = EntradaSalida.query
    registros = consulta.order_by(EntradaSalida.creado.desc()).offset(start).limit(rows_per_page).all()
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
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }
