"""
Archivo Documentos Solicitudes, vistas
"""
import json
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.permisos.models import Permiso


MODULO = "ARC ARCHIVOS"

# Roles necesarios
ROL_JEFE_REMESA = "ARCHIVO JEFE REMESA"
ROL_ARCHIVISTA = "ARCHIVO ARCHIVISTA"
ROL_SOLICITANTE = "ARCHIVO SOLICITANTE"
ROL_RECEPCIONISTA = "ARCHIVO RECEPCIONISTA"

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
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
            rol_archivista=ROL_ARCHIVISTA,
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
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
        )
    if ROL_JEFE_REMESA in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True}),
            filtros_remesas=json.dumps({"estatus": "A", "omitir_archivados": True, "omitir_cancelados": True, "omitir_pendientes": True}),
            estatus="A",
            titulo="Archivo - Bandeja de Entrada 📥",
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
            rol_archivista=ROL_ARCHIVISTA,
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
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
            rol_archivista=ROL_ARCHIVISTA,
        )
    # Por defecto
    return render_template(
        "arc_archivos/list.jinja2",
        filtros=json.dumps({"estatus": "A", "omitir_archivados": True, "juzgado_id": current_user.autoridad.id}),
        estatus="A",
        titulo="Archivo - Bandeja de Entrada 📥",
        estados_solicitudes=ArcSolicitud.ESTADOS,
        estados_remesas=ArcRemesa.ESTADOS,
        tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
    )


@arc_archivos.route("/arc_archivos/historial")
def list_history():
    """Listado de Archivo en el Historial (están_archivados)"""

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()

    if current_user.can_admin(MODULO):
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
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
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
        )
    if ROL_JEFE_REMESA in current_user_roles:
        return render_template(
            "arc_archivos/list_jefe_remesa.jinja2",
            filtros_solicitudes=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True}),
            filtros_remesas=json.dumps({"estatus": "A", "mostrar_archivados": True, "omitir_cancelados": True, "orden_acendente": True}),
            estatus="A",
            titulo="Archivo - Historial 🗃️",
            mostrando_historial=True,
            estados_solicitudes=ArcSolicitud.ESTADOS,
            estados_remesas=ArcRemesa.ESTADOS,
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
            rol_archivista=ROL_ARCHIVISTA,
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
            tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
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
        tipos_documentos_remesas=ArcRemesa.TIPOS_DOCUMENTOS,
    )
