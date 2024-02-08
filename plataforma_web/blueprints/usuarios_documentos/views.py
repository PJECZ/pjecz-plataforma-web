"""
Usuarios Documentos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_curp

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_documentos.models import UsuarioDocumento

from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud

MODULO = "USUARIOS DOCUMENTOS"

CAMPOS = [
    "IDENTIFICACION",
    "CP FISCAL",
    "DOMICILIO",
    "ES MADRE",
    "ESTUDIOS",
    "ESTADO CIVIL",
    "TELEFONO",
    "EMAIL",
]

usuarios_documentos = Blueprint("usuarios_documentos", __name__, template_folder="templates")


@usuarios_documentos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_documentos.route("/usuarios_documentos/datatable_json", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def datatable_json():
    """DataTable JSON para listado de Usuarios Documentos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioDocumento.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(UsuarioDocumento.modificado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario.id),
                },
                "nombre": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios_documentos.detail", usuario_documento_id=resultado.id),
                },
                "curp": resultado.curp,
                "estado": resultado.estado_general,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_documentos.route("/usuarios_documentos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_active():
    """Listado de Usuarios Documentos activos"""
    return render_template(
        "usuarios_documentos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios Documentos",
        estatus="A",
        estados=UsuarioDocumento.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_documentos.route("/usuarios_documentos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Usuarios Documentos inactivos"""
    return render_template(
        "usuarios_documentos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios Documentos inactivos",
        estatus="B",
        estados=UsuarioDocumento.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_documentos.route("/usuarios_documentos/<int:usuario_documento_id>")
def detail(usuario_documento_id):
    """Detalle de un Usuario Documento"""
    usuario_documento = UsuarioDocumento.query.get_or_404(usuario_documento_id)
    return render_template("usuarios_documentos/detail.jinja2", usuario_documento=usuario_documento)


@usuarios_documentos.route("/usuarios_documentos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Usuario Documento vacío"""
    curp = None
    try:
        curp = safe_curp(current_user.curp)
    except ValueError:
        flash("CURP no válida, no puede ingresar a este módulo sin una CURP.", "warning")
        return redirect(url_for("sistemas.start"))
    # Buscar si el usuario ya tiene un registro previo
    usuario_documento = UsuarioDocumento.query.filter_by(curp=curp).first()
    # Si no cuenta con un registro previo, crear uno nuevo vacío
    if usuario_documento is None:
        usuario_documento = UsuarioDocumento(
            usuario=current_user,
            curp=current_user.curp,
        ).save()

        # Copiar teléfono y email personales de la tabla de usuarios_solicitudes
        usuario_solicitud = UsuarioSolicitud.query.filter_by(usuario=current_user).first()
        if usuario_solicitud:
            usuario_documento.telefono_personal = usuario_solicitud.telefono_celular
            usuario_documento.email_personal = usuario_solicitud.email_personal
            # Si ya están validados también copiar su validación
            if usuario_solicitud.validacion_telefono_celular is True:
                usuario_documento.estado_telefono = "VALIDO"
            elif usuario_solicitud.telefono_celular == "":
                usuario_documento.estado_telefono = "NO VALIDO"
            elif usuario_solicitud.telefono_celular != "":
                usuario_documento.estado_telefono = "POR VALIDAR"
            if usuario_solicitud.validacion_email is True:
                usuario_documento.estado_email = "VALIDO"
            elif usuario_solicitud.email_personal == "":
                usuario_documento.estado_email = "NO VALIDO"
            elif usuario_solicitud.email_personal != "":
                usuario_documento.estado_email = "POR VALIDAR"
        # Guardar registro
        usuario_documento.save()
    # Redirigirlo al detalle
    return redirect(url_for("usuarios_documentos.detail", usuario_documento_id=usuario_documento.id))


@usuarios_documentos.route("/usuarios_documentos/editar/identificacion/<int:usuario_documento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_identificacion(usuario_documento_id):
    """Detalle de un Usuario Documento"""
    usuario_documento = UsuarioDocumento.query.get_or_404(usuario_documento_id)
    return render_template("usuarios_documentos/edit_identificacion.jinja2", usuario_documento=usuario_documento)


@usuarios_documentos.route("/usuarios_documentos/validar/identificacion/<int:usuario_documento_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_identificacion(usuario_documento_id):
    """Detalle de un Usuario Documento"""
    usuario_documento = UsuarioDocumento.query.get_or_404(usuario_documento_id)
    return render_template("usuarios_documentos/validate_identificacion.jinja2", usuario_documento=usuario_documento)
