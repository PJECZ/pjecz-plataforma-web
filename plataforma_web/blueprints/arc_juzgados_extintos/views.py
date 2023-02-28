"""
Archivo Juzgados Extintos, vistas
"""
from flask import Blueprint
from flask_login import login_required
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_juzgados_extintos.models import ArcJuzgadoExtinto
from plataforma_web.blueprints.permisos.models import Permiso


MODULO = "ARC JUZGADOS EXTINTOS"

arc_juzgados_extintos = Blueprint("arc_juzgados_extintos", __name__, template_folder="templates")


@arc_juzgados_extintos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""
