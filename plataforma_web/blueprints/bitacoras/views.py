"""
Bitácoras, vistas
"""
import json
from flask import Blueprint, render_template, request
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora

bitacoras = Blueprint("bitacoras", __name__, template_folder="templates")

CONSULTAS_LIMITE = 800


@bitacoras.route("/bitacoras")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def list_active():
    """Listado de bitácoras"""
    bitacoras_activas = Bitacora.query.order_by(Bitacora.creado.desc()).limit(CONSULTAS_LIMITE).all()
    return render_template("bitacoras/list.jinja2", bitacoras=bitacoras_activas)


@bitacoras.route("/bitacoras/ajax")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def ajax():
    """AJAX para listado de bitácoras"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.args.get("draw"))  # Número de Página
        start = int(request.args.get("start"))  # Registro inicial
        rows_per_page = int(request.args.get("length"))  # Renglones por página
    except ValueError:
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    bitacoras_activas = Bitacora.query.order_by(Bitacora.creado.desc()).offset(start).limit(rows_per_page).all()
    total = Bitacora.query.count()

    # Listado de diccionarios
    bitacoras_data = [{"creado": bitacora.creado.strftime("%Y-%m-%d %H:%M:%S"), "usuario_email": bitacora.usuario.email, "modulo": bitacora.modulo, "descripcion": bitacora.descripcion, "url": bitacora.url} for bitacora in bitacoras_activas]

    return json.dumps(
        {
            "draw": draw,
            "iTotalRecords": total,
            "iTotalDisplayRecords": total,
            "aaData": bitacoras_data,
        }
    )
