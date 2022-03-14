"""
Bitácoras, vistas
"""
from flask import Blueprint, render_template, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "BITACORAS"

bitacoras = Blueprint("bitacoras", __name__, template_folder="templates")


@bitacoras.route("/bitacoras/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.VER)
def datatable_json():
    """DataTable JSON para listado de listado de bitácoras"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Bitacora.query
    registros = consulta.order_by(Bitacora.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar un listado de diccionarios
    data = []
    for bitacora in registros:
        data.append(
            {
                "creado": bitacora.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": {
                    "email": bitacora.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=bitacora.usuario_id),
                },
                "vinculo": {
                    "descripcion": bitacora.descripcion,
                    "url": bitacora.url,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@bitacoras.route("/bitacoras")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de bitácoras"""
    return render_template("bitacoras/list.jinja2")
