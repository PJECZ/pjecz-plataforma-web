"""
Usuarios Nóminas, vistas
"""
import json
from flask import Blueprint, render_template, request, flash, make_response, redirect, url_for, current_app
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.exceptions import MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError
from lib.google_cloud_storage import get_blob_name_from_url, get_file_from_gcs
from lib.safe_string import safe_curp

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_nominas.models import UsuarioNomina

MODULO = "USUARIOS NOMINAS"

usuarios_nominas = Blueprint("usuarios_nominas", __name__, template_folder="templates")


@usuarios_nominas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_nominas.route("/usuarios_nominas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuario Nómina"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioNomina.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter(UsuarioNomina.usuario_id == current_user.id)
    registros = consulta.order_by(UsuarioNomina.fecha.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                    "descripcion": resultado.descripcion,
                },
                "pdf": {
                    "archivo_pdf": resultado.archivo_pdf,
                    "url_pdf": url_for("usuarios_nominas.download_pdf", usuario_nomina_id=resultado.id),
                },
                "xml": {
                    "archivo_xml": resultado.archivo_xml,
                    "url_xml": url_for("usuarios_nominas.download_xml", usuario_nomina_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_nominas.route("/usuarios_nominas")
def list_active():
    """Listado de Usuarios Nóminas activos"""

    curp = ""
    try:
        curp = safe_curp(current_user.curp)
    except ValueError:
        curp = ""

    if curp == "":
        return render_template(
            "usuarios_solicitudes/message.jinja2",
            usuario=current_user,
            mensaje="Tenemos un problema con tu CURP en Plataforma Web. Puede ser que falte o que sea incorrecto. Por favor por medio de un ticket de soporte haznos llegar tu CURP correcto (18 caracteres).",
            btn_texto="Crear ticket",
            btn_enlace=url_for("soportes_tickets.new"),
        )

    return render_template(
        "usuarios_nominas/list.jinja2",
        filtros=json.dumps({"usuario_id": current_user.id, "estatus": "A"}),
        titulo=f"Recibos de Nómina para {current_user.nombre}",
        estatus="A",
    )


@usuarios_nominas.route("/usuarios_nominas/<int:usuario_nomina_id>/pdf")
def download_pdf(usuario_nomina_id):
    """Descargar el archivo PDF de un Timbrado"""

    # Consultar el Timbrado
    usuario_nomina = UsuarioNomina.query.get_or_404(usuario_nomina_id)

    # Seguridad de liga
    if usuario_nomina.usuario.curp != current_user.curp:
        flash("Acceso no autorizado", "warning")
        return redirect(url_for("usuarios_nominas.list_active"))

    # Si no tiene URL, redirigir a la página de detalle
    if usuario_nomina.url_pdf == "":
        flash("El usuario_nomina no tiene un archivo PDF", "warning")
        return redirect(url_for("usuarios_nominas.list_active"))

    # Si no tiene nombre para el archivo en archivo_pdf, elaborar uno con el UUID
    descarga_nombre = usuario_nomina.archivo_pdf
    if descarga_nombre == "":
        descarga_nombre = f"{usuario_nomina.tfd_uuid}.pdf"

    # Obtener el contenido del archivo desde Google Storage
    try:
        descarga_contenido = get_file_from_gcs(
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_PERSEO"],
            blob_name=get_blob_name_from_url(usuario_nomina.url_pdf),
        )
    except (MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError) as error:
        flash(str(error), "danger")
        return redirect(url_for("usuarios_nominas.detail", usuario_nomina_id=usuario_nomina.id))

    # Descargar un archivo PDF
    response = make_response(descarga_contenido)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={descarga_nombre}"
    return response


@usuarios_nominas.route("/usuarios_nominas/<int:usuario_nomina_id>/xml")
def download_xml(usuario_nomina_id):
    """Descargar el archivo XML de un Timbrado"""

    # Consultar el Timbrado
    usuario_nomina = UsuarioNomina.query.get_or_404(usuario_nomina_id)

    # Seguridad de liga
    if usuario_nomina.usuario.curp != current_user.curp:
        flash("Acceso no autorizado", "warning")
        return redirect(url_for("usuarios_nominas.list_active"))

    # Si no tiene URL, redirigir a la página de detalle
    if usuario_nomina.url_xml == "":
        flash("El usuario_nomina no tiene un archivo XML", "warning")
        return redirect(url_for("usuarios_nominas.list_active"))

    # Si no tiene nombre para el archivo en archivo_xml, elaborar uno con el UUID
    descarga_nombre = usuario_nomina.archivo_xml
    if descarga_nombre == "":
        descarga_nombre = f"{usuario_nomina.tfd_uuid}.xml"

    # Obtener el contenido del archivo desde Google Storage
    try:
        descarga_contenido = get_file_from_gcs(
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_PERSEO"],
            blob_name=get_blob_name_from_url(usuario_nomina.url_xml),
        )
    except (MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError) as error:
        flash(str(error), "danger")
        return redirect(url_for("usuarios_nominas.detail", usuario_nomina_id=usuario_nomina.id))

    # Descargar un archivo XML
    response = make_response(descarga_contenido)
    response.headers["Content-Type"] = "text/xml"
    response.headers["Content-Disposition"] = f"attachment; filename={descarga_nombre}"
    return response
