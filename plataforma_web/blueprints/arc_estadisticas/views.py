"""
ARC Estadísticas, vistas
"""
import json
from datetime import date, timedelta
from flask import Blueprint, render_template, request, url_for, flash, redirect
from flask_login import current_user, login_required

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_estadisticas.forms import ArcEstadisticasForm
from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa

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


@arc_estadisticas.route("/arc_estadisticas/report_solicitudes_remesas", methods=["GET", "POST"])
def report_solicitudes_remesas():
    """Elaborar reporte de Solicitudes y Remesas"""
    # Preparar el formulario
    form = ArcEstadisticasForm()
    # return render_template("arc_estadisticas/report_solicitudes_remesas.jinja2", form=form)
    fecha_desde = date.today().replace(day=1)
    fecha_hasta = date.today()
    # Si viene el formulario
    if form.validate():
        # Tomar los valores del formulario
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        # Si la fecha_desde es posterior a la fecha_hasta, se intercambian
        if fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde
    else:
        form.fecha_desde.data = fecha_desde
        form.fecha_hasta.data = fecha_hasta
    # Cálculos estadísticos
    solicitudes = ArcSolicitud.query.filter(ArcSolicitud.creado >= fecha_desde).filter(ArcSolicitud.creado <= fecha_hasta).filter_by(estatus="A").filter(ArcSolicitud.estado != "CANCELADO").count()
    remesas = ArcRemesa.query.filter(ArcRemesa.creado >= fecha_desde).filter(ArcRemesa.creado <= fecha_hasta).filter_by(estatus="A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE").count()
    # Entregar el reporte
    return render_template(
        "arc_estadisticas/report_solicitudes_remesas.jinja2",
        solicitudes=solicitudes,
        remesas=remesas,
        filtros_por_distrito=json.dumps(
            {
                "estatus": "A",
                "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
            }
        ),
        form=form,
    )
