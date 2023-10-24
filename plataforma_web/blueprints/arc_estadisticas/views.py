"""
ARC Estadísticas, vistas
"""
from flask import Blueprint, render_template, request, url_for
from flask_login import current_user, login_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_estadisticas.forms import ArcEstadisticasForm

MODULO = "ARC ESTADISTICAS"

arc_estadisticas = Blueprint("arc_estadisticas", __name__, template_folder="templates")


@arc_estadisticas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_estadisticas.route("/arc_estadisticas/")
def indice():
    """Detalle de un Modulo"""
    return render_template("arc_estadisticas/indice.jinja2")


@arc_estadisticas.route("/arc_estadisticas/report_solicitudes_remesas")
def report_solicitudes_remesas():
    """Detalle de un Modulo"""
    form = ArcEstadisticasForm()
    return render_template("arc_estadisticas/report_solicitudes_remesas.jinja2", form=form)
