"""
Bitácoras, vistas
"""
from flask import Blueprint, render_template, request
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora

bitacoras = Blueprint("bitacoras", __name__, template_folder="templates")


@bitacoras.route("/bitacoras")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def list_active():
    """Listado de bitácoras"""
    return render_template("bitacoras/list.jinja2")


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
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    bitacoras_activas = Bitacora.query.order_by(Bitacora.creado.desc()).offset(start).limit(rows_per_page).all()
    total = Bitacora.query.count()

    # Elaborar un listado de diccionarios
    bitacoras_data = []
    for bitacora in bitacoras_activas:
        bitacoras_data.append({
            "creado": bitacora.creado.strftime("%Y-%m-%d %H:%M:%S"),
            "usuario_email": bitacora.usuario.email,
            "modulo": bitacora.modulo,
            "vinculo": {
                "descripcion": bitacora.descripcion,
                "url": bitacora.url,
            }
        })

    # Entregar (desde Flask 1.1.0 un diccionario se convierte en JSON automáticamente)
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": bitacoras_data,
    }
