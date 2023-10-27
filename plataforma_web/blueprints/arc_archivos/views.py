"""
Archivo Documentos Solicitudes, vistas
"""
import json
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from sqlalchemy.sql.functions import count

from lib.datatables import get_datatable_parameters, output_datatable_json

from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad

from plataforma_web.blueprints.arc_archivos.forms import ArcEstadisticasDateRangeForm

MODULO = "ARC ARCHIVOS"

# Roles necesarios
ROL_JEFE_REMESA = "ARCHIVO JEFE REMESA"
ROL_JEFE_REMESA_ADMINISTRADOR = "ARCHIVO JEFE REMESA ADMINISTRADOR"
ROL_ARCHIVISTA = "ARCHIVO ARCHIVISTA"
ROL_SOLICITANTE = "ARCHIVO SOLICITANTE"
ROL_RECEPCIONISTA = "ARCHIVO RECEPCIONISTA"
ROL_LEVANTAMENTISTA = "ARCHIVO LEVANTAMENTISTA"

arc_archivos = Blueprint("arc_archivos", __name__, template_folder="templates")


@arc_archivos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_archivos.route("/arc_archivos")
def list_active():
    """Listado de Archivo"""

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()

    if current_user.can_admin(MODULO):
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
            mostrar_btn_local_global="LOCAL",
            mostrar_btn_historial="IR_AL_HISTORIAL",
            mostrar_btn_estadistica=True,
        )
    if ROL_JEFE_REMESA_ADMINISTRADOR in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "sede": current_user.autoridad.sede}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "omitir_pendientes": True, "sede": current_user.autoridad.sede}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
            mostrar_btn_local_global="LOCAL",
            mostrar_btn_historial="IR_AL_HISTORIAL",
            mostrar_btn_estadistica=True,
        )
    if ROL_JEFE_REMESA in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "sede": current_user.autoridad.sede}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "omitir_pendientes": True, "sede": current_user.autoridad.sede}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
            mostrar_btn_historial="IR_AL_HISTORIAL",
        )
    if ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
        return render_template(
            "arc_archivos/list_solicitante.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "juzgado_id": current_user.autoridad.id}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "juzgado_id": current_user.autoridad.id}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
        )
    if ROL_ARCHIVISTA in current_user_roles:
        return render_template(
            "arc_archivos/list_archivista.jinja2",
            filtros_solicitudes=json.dumps({"asignado_id": current_user.id, "estatus": "A", "omitir_archivados": True}),
            filtros_remesas=json.dumps({"asignado_id": current_user.id, "estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "omitir_pendientes": True}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
        )
    # Por defecto
    return render_template(
        "arc_archivos/list.jinja2",
        filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "juzgado_id": current_user.autoridad.id}),
        filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "juzgado_id": current_user.autoridad.id}),
        estatus="A",
        titulo="Archivo - Bandeja de Entrada 📥",
        estados_solicitudes=ArcSolicitud.ESTADOS,
        estados_remesas=ArcRemesa.ESTADOS,
    )


@arc_archivos.route("/arc_archivos/historial")
def list_history():
    """Listado de Archivo en el Historial (están_archivados)"""

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()

    if current_user.can_admin(MODULO):
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": False, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": False, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            mostrar_btn_local_global="LOCAL",
            mostrar_btn_historial="IR_A_ACTIVOS",
        )
    if ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
        return render_template(
            "arc_archivos/list_solicitante.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "juzgado_id": current_user.autoridad.id, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "juzgado_id": current_user.autoridad.id, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
        )
    if ROL_JEFE_REMESA_ADMINISTRADOR in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True, "sede": current_user.autoridad.sede}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True, "sede": current_user.autoridad.sede}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
            mostrar_btn_local_global="LOCAL",
            mostrar_btn_historial="IR_A_ACTIVOS",
        )
    if ROL_JEFE_REMESA in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True, "sede": current_user.autoridad.sede}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True, "sede": current_user.autoridad.sede}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
            mostrar_btn_historial="IR_A_ACTIVOS",
        )
    if ROL_ARCHIVISTA in current_user_roles:
        return render_template(
            "arc_archivos/list_archivista.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "asignado_id": current_user.id, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "asignado_id": current_user.id, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            rol_archivista=ROL_ARCHIVISTA,
        )
    # Por defecto
    return render_template(
        "arc_archivos/list.jinja2",
        filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "juzgado_id": current_user.autoridad.id, "orden_acendente": True}),
        filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "juzgado_id": current_user.autoridad.id, "orden_acendente": True}),
        estatus="A",
        titulo="Archivo - Historial 🗃️",
        mostrando_historial=True,
        estados_solicitudes=ArcSolicitud.ESTADOS,
        estados_remesas=ArcRemesa.ESTADOS,
    )


@arc_archivos.route("/arc_archivos/todos/<int:historial>", methods=["GET", "POST"])
def list_all(historial):
    """Listado de Archivo de todos los distritos (Solo para Jefes de Remesa Administradores)"""

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()

    # Si no tiene el rol de JEFE DE REMESA ADMINISTRADOR es redireccionado al listado normal
    if ROL_JEFE_REMESA_ADMINISTRADOR not in current_user_roles or not current_user.can_admin(MODULO):
        redirect(url_for("arc_archivos.list_active"))

    # Extraemos los distritos
    sedes = [
        {"id": "ND", "nombre": "NO DEFINIDO"},
        {"id": "DACN", "nombre": "ACUÑA"},
        {"id": "DMNC", "nombre": "MONCLOVA"},
        {"id": "DPRR", "nombre": "PARRAS"},
        {"id": "DRGR", "nombre": "REGION CARBONIFERA"},
        {"id": "DSBN", "nombre": "SABINAS"},
        {"id": "DSLT", "nombre": "SALTILLO"},
        {"id": "DSPD", "nombre": "SAN PEDRO"},
        {"id": "DTRC", "nombre": "TORREÓN"},
    ]

    if historial == 1:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            mostrar_btn_local_global="GLOBAL",
            mostrar_btn_historial="IR_A_ACTIVOS",
            sedes=sedes,
        )

    return render_template(
        "arc_archivos/list_jefe_remesa.jinja2",
        filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True}),
        filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_pendientes": True}),
        estatus="A",
        titulo="Archivo - Bandeja de Entrada 📥",
        estados_solicitudes=ArcSolicitud.ESTADOS,
        estados_remesas=ArcRemesa.ESTADOS,
        rol_archivista=ROL_ARCHIVISTA,
        mostrar_btn_local_global="GLOBAL",
        mostrar_btn_historial="IR_AL_HISTORIAL",
        sedes=sedes,
    )


@arc_archivos.route("/arc_archivos/estadisticas")
def stats():
    """Detalle de la página index de estadísticas"""
    form_rango_fechas = ArcEstadisticasDateRangeForm()
    form_rango_fechas.fecha_desde.data = date.today().replace(day=1)
    form_rango_fechas.fecha_hasta.data = date.today()
    return render_template("arc_archivos/stats.jinja2", form=form_rango_fechas)


@arc_archivos.route("/arc_archivos/estadisticas/solicitudes", methods=["GET", "POST"])
def stats_solicitudes():
    """Estadísticas de Solicitudes por Totales, Distritos e Instancias"""
    form = ArcEstadisticasDateRangeForm()
    # Validar formulario
    if form.validate():
        # Tomar los valores del formulario
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        # Si la fecha_desde es posterior a la fecha_hasta, se intercambian
        if fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde
        # Case para botones de reportes
        if "totales" in request.form:
            # Cálculo de solicitudes totales
            solicitudes = ArcSolicitud.query.filter(ArcSolicitud.creado >= fecha_desde).filter(ArcSolicitud.creado <= fecha_hasta).filter_by(estatus="A").filter(ArcSolicitud.estado != "CANCELADO").count()
            return render_template(
                "arc_archivos/stats_solicitudes_totales.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                solicitudes=solicitudes,
            )
        elif "por_distritos" in request.form:
            return render_template(
                "arc_archivos/stats_solicitudes_por_distritos.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filtros_por_distritos=json.dumps(
                    {
                        "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                        "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
                    }
                ),
            )
        elif "por_instancias" in request.form:
            return render_template(
                "arc_archivos/stats_solicitudes_por_instancias.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filtros_por_instancias=json.dumps(
                    {
                        "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                        "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
                    }
                ),
            )
    # Redirigimos a página índice de estadísticas
    return redirect(url_for("arc_archivos.stats"))


@arc_archivos.route("/arc_archivos/estadisticas/remesas", methods=["GET", "POST"])
def stats_remesas():
    """Estadísticas de Remesas por Totales, Distritos e Instancias"""
    form = ArcEstadisticasDateRangeForm()
    # Validar formulario
    if form.validate():
        # Tomar los valores del formulario
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        # Si la fecha_desde es posterior a la fecha_hasta, se intercambian
        if fecha_desde > fecha_hasta:
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde
        # Case para botones de reportes
        if "totales" in request.form:
            # Cálculo de solicitudes totales
            remesas = ArcRemesa.query.filter(ArcRemesa.creado >= fecha_desde).filter(ArcRemesa.creado <= fecha_hasta).filter_by(estatus="A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE").count()
            return render_template(
                "arc_archivos/stats_remesas_totales.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                remesas=remesas,
            )
        elif "por_distritos" in request.form:
            return render_template(
                "arc_archivos/stats_remesas_por_distritos.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filtros_por_distritos=json.dumps(
                    {
                        "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                        "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
                    }
                ),
            )
        elif "por_instancias" in request.form:
            return render_template(
                "arc_archivos/stats_remesas_por_instancias.jinja2",
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filtros_por_instancias=json.dumps(
                    {
                        "fecha_desde": fecha_desde.strftime("%Y-%m-%d"),
                        "fecha_hasta": fecha_hasta.strftime("%Y-%m-%d"),
                    }
                ),
            )
    # Redirigimos a página índice de estadísticas
    return redirect(url_for("arc_archivos.stats"))


@arc_archivos.route("/arc_archivos/datatable_json_solicitudes_por_distrito", methods=["GET", "POST"])
def datatable_json_solicitudes_por_distrito():
    """DataTable JSON para listado de solicitudes y remesas por distrito"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Dos columnas en la consulta
    consulta = database.query(
        Distrito.nombre_corto.label("distritos"),
        count("*").label("solicitudes"),
    )
    # Consultar
    consulta = consulta.select_from(Autoridad).join(ArcSolicitud).join(Distrito)
    consulta = consulta.filter(Distrito.es_distrito == True).filter(Distrito.es_distrito_judicial == True).filter(Distrito.es_jurisdiccional == True)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ArcSolicitud.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ArcSolicitud.creado <= request.form["fecha_hasta"])
    consulta = consulta.filter(Autoridad.estatus == "A").filter(ArcSolicitud.estatus == "A").filter(Distrito.estatus == "A").filter(ArcSolicitud.estado != "CANCELADO")
    consulta = consulta.group_by(Distrito.nombre_corto)
    consulta = consulta.order_by(Distrito.nombre_corto)
    resultado = consulta.offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for registro in resultado:
        data.append(
            {
                "distritos": registro.distritos,
                "solicitudes": registro.solicitudes,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_archivos.route("/arc_archivos/datatable_json_remesas_por_distrito", methods=["GET", "POST"])
def datatable_json_remesas_por_distrito():
    """DataTable JSON para listado de remesas y remesas por distrito"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Dos columnas en la consulta
    consulta = database.query(
        Distrito.nombre_corto.label("distritos"),
        count("*").label("remesas"),
    )
    # Consultar
    consulta = consulta.select_from(Autoridad).join(ArcRemesa).join(Distrito)
    consulta = consulta.filter(Distrito.es_distrito == True).filter(Distrito.es_distrito_judicial == True).filter(Distrito.es_jurisdiccional == True)
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ArcRemesa.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ArcRemesa.creado <= request.form["fecha_hasta"])
    consulta = consulta.filter(Autoridad.estatus == "A").filter(ArcRemesa.estatus == "A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE")
    consulta = consulta.group_by(Distrito.nombre_corto)
    consulta = consulta.order_by(Distrito.nombre_corto)
    resultado = consulta.offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for registro in resultado:
        data.append(
            {
                "distritos": registro.distritos,
                "remesas": registro.remesas,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_archivos.route("/arc_archivos/datatable_json_solicitudes_por_instancias", methods=["GET", "POST"])
def datatable_json_solicitudes_por_instancias():
    """DataTable JSON para listado de solicitudes y remesas por instancias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Dos columnas en la consulta
    consulta = database.query(
        Autoridad.clave.label("juzgados"),
        count("*").label("solicitudes"),
    )
    # Consultar
    consulta = consulta.select_from(Autoridad).join(ArcSolicitud)
    consulta = consulta.filter(Autoridad.es_archivo_solicitante == True).filter(Autoridad.estatus == "A")
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ArcSolicitud.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ArcSolicitud.creado <= request.form["fecha_hasta"])
    consulta = consulta.filter(ArcSolicitud.estatus == "A").filter(ArcSolicitud.estado != "CANCELADO")
    consulta = consulta.group_by(Autoridad.clave)
    consulta = consulta.order_by(Autoridad.clave)
    resultado = consulta.offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for registro in resultado:
        data.append(
            {
                "instancias": registro.juzgados,
                "solicitudes": registro.solicitudes,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_archivos.route("/arc_archivos/datatable_json_remesas_por_instancias", methods=["GET", "POST"])
def datatable_json_remesas_por_instancias():
    """DataTable JSON para listado de remesas y remesas por instancias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # SQLAlchemy database session
    database = current_app.extensions["sqlalchemy"].db.session
    # Dos columnas en la consulta
    consulta = database.query(
        Autoridad.clave.label("juzgados"),
        count("*").label("remesas"),
    )
    # Consultar
    consulta = consulta.select_from(Autoridad).join(ArcRemesa)
    consulta = consulta.filter(Autoridad.es_archivo_solicitante == True).filter(Autoridad.estatus == "A")
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ArcRemesa.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ArcRemesa.creado <= request.form["fecha_hasta"])
    consulta = consulta.filter(ArcRemesa.estatus == "A").filter(ArcRemesa.estatus == "A").filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "PENDIENTE")
    consulta = consulta.group_by(Autoridad.clave)
    consulta = consulta.order_by(Autoridad.clave)
    resultado = consulta.offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for registro in resultado:
        data.append(
            {
                "instancias": registro.juzgados,
                "remesas": registro.remesas,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)
