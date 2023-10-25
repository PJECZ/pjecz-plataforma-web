"""
ARC Estadísticas, vistas
"""
import json
from datetime import date, timedelta
from flask import current_app, Blueprint, render_template, request, url_for, flash, redirect
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.sql.functions import count

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_estadisticas.forms import ArcEstadisticasForm
from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad

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
        filtros_por_distritos=json.dumps(
            {
                "estatus": "A",
                "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
            }
        ),
        filtros_por_juzgados=json.dumps(
            {
                "estatus": "A",
                "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
            }
        ),
        form=form,
    )


@arc_estadisticas.route("/arc_estadisticas/datatable_json_solicitudes_remesas_por_distrito", methods=["GET", "POST"])
def datatable_json_solicitudes_remesas_distrito():
    """DataTable JSON para listado de solicitudes y remesas por distrito"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Consultar
    # Dos columnas en la consulta
    consulta_solicitudes = database.query(
        Distrito.nombre_corto.label("distritos"),
        count("*").label("solicitudes"),
    )
    # Consultar
    consulta_solicitudes = consulta_solicitudes.select_from(Autoridad).join(ArcSolicitud).join(Distrito)
    consulta_solicitudes = consulta_solicitudes.filter(Distrito.es_distrito == True).filter(Distrito.es_distrito_judicial == True).filter(Distrito.es_jurisdiccional == True)
    if "fecha_desde" in request.form:
        consulta_solicitudes = consulta_solicitudes.filter(ArcSolicitud.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta_solicitudes = consulta_solicitudes.filter(ArcSolicitud.creado <= request.form["fecha_hasta"])
    consulta_solicitudes = consulta_solicitudes.filter(Autoridad.estatus == "A").filter(ArcSolicitud.estatus == "A").filter(Distrito.estatus == "A").filter(ArcSolicitud.estado != "CANCELADO")
    consulta_solicitudes = consulta_solicitudes.group_by(Distrito.nombre_corto)
    consulta_solicitudes = consulta_solicitudes.order_by(Distrito.nombre_corto)
    resultado_solicitudes = consulta_solicitudes.all()
    total = consulta_solicitudes.count()
    # Elaborar datos para DataTable
    data = []
    for registro in resultado_solicitudes:
        data.append(
            {
                "nombre_corto": registro.distritos,
                "solicitudes": registro.solicitudes,
                "remesas": "-",
            }
        )
    # Consulta para Remesa
    consulta_remesas = database.query(
        Distrito.nombre_corto.label("distritos"),
        count("*").label("remesas"),
    )
    # Consultar
    consulta_remesas = consulta_remesas.select_from(Autoridad).join(Distrito).join(ArcRemesa)
    consulta_remesas = consulta_remesas.filter(Distrito.es_distrito == True).filter(Distrito.es_distrito_judicial == True).filter(Distrito.es_jurisdiccional == True)
    if "fecha_desde" in request.form:
        consulta_remesas = consulta_remesas.filter(ArcRemesa.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta_remesas = consulta_remesas.filter(ArcRemesa.creado <= request.form["fecha_hasta"])
    consulta_remesas = consulta_remesas.filter(Autoridad.estatus == "A").filter(ArcRemesa.estatus == "A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE")
    consulta_remesas = consulta_remesas.group_by(Distrito.nombre_corto)
    consulta_remesas = consulta_remesas.order_by(Distrito.nombre_corto)
    resultado_remesas = consulta_remesas.all()
    # Elaborar datos para DataTable
    for registro in resultado_remesas:
        encontrado = False
        for item in data:
            if item["nombre_corto"] == registro.distritos:
                item["remesas"] = registro.remesas
                encontrado = True
        if not encontrado:
            data.append(
                {
                    "nombre_corto": registro.distritos,
                    "solicitudes": "-",
                    "remesas": registro.remesas,
                }
            )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_estadisticas.route("/arc_estadisticas/datatable_json_solicitudes_remesas_por_juzgado", methods=["GET", "POST"])
def datatable_json_solicitudes_remesas_juzgado():
    """DataTable JSON para listado de solicitudes y remesas por Juzgado"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Consulta para Solicitudes
    consulta_solicitudes = database.query(
        Autoridad.clave.label("juzgados"),
        count("*").label("solicitudes"),
    )
    # Juntar las tablas sentencias y materias_tipos_juicios
    consulta_solicitudes = consulta_solicitudes.select_from(Autoridad).join(ArcSolicitud)
    consulta_solicitudes = consulta_solicitudes.filter(Autoridad.es_archivo_solicitante == True)
    if "fecha_desde" in request.form:
        consulta_solicitudes = consulta_solicitudes.filter(ArcSolicitud.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta_solicitudes = consulta_solicitudes.filter(ArcSolicitud.creado <= request.form["fecha_hasta"])
    consulta_solicitudes = consulta_solicitudes.filter(Autoridad.estatus == "A").filter(ArcSolicitud.estatus == "A").filter(ArcSolicitud.estado != "CANCELADO")
    consulta_solicitudes = consulta_solicitudes.group_by(Autoridad.clave)
    consulta_solicitudes = consulta_solicitudes.order_by(Autoridad.clave)
    resultado_solicitudes = consulta_solicitudes.all()
    total = consulta_solicitudes.count()

    # Elaborar datos para DataTable
    data = []
    for registro in resultado_solicitudes:
        data.append(
            {
                "clave": registro.juzgados,
                "solicitudes": registro.solicitudes,
                "remesas": "-",
            }
        )
    # Consulta para Remesa
    consulta_remesas = database.query(
        Autoridad.clave.label("juzgados"),
        count("*").label("remesas"),
    )
    # Consultar
    consulta_remesas = consulta_remesas.select_from(Autoridad).join(ArcRemesa)
    consulta_remesas = consulta_remesas.filter(Autoridad.es_archivo_solicitante == True)
    if "fecha_desde" in request.form:
        consulta_remesas = consulta_remesas.filter(ArcRemesa.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta_remesas = consulta_remesas.filter(ArcRemesa.creado <= request.form["fecha_hasta"])
    consulta_remesas = consulta_remesas.filter(Autoridad.estatus == "A").filter(ArcRemesa.estatus == "A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE")
    consulta_remesas = consulta_remesas.group_by(Autoridad.clave)
    consulta_remesas = consulta_remesas.order_by(Autoridad.clave)
    resultado_remesas = consulta_remesas.all()
    # ---

    # Elaborar datos para DataTable
    for registro in resultado_remesas:
        encontrado = False
        for item in data:
            if item["clave"] == registro.juzgados:
                item["remesas"] = registro.remesas
                encontrado = True
        if not encontrado:
            data.append(
                {
                    "clave": registro.juzgados,
                    "solicitudes": "-",
                    "remesas": registro.remesas,
                }
            )
    # Entregar JSON
    return output_datatable_json(draw, total, data)
