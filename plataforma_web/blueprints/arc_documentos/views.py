"""
Archivo Documentos, vistas
"""
import json
import os
import requests
from datetime import date
from dotenv import load_dotenv

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_expediente, safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.arc_documentos.forms import (
    ArcDocumentoNewArchivoForm,
    ArcDocumentoNewSolicitanteForm,
    ArcDocumentoEditArchivoForm,
    ArcDocumentoEditSolicitanteForm,
)

from plataforma_web.blueprints.arc_archivos.views import (
    ROL_JEFE_REMESA,
    ROL_ARCHIVISTA,
    ROL_SOLICITANTE,
    ROL_RECEPCIONISTA,
)


MODULO = "ARC DOCUMENTOS"

arc_documentos = Blueprint("arc_documentos", __name__, template_folder="templates")


@arc_documentos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_documentos.route("/arc_documentos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Documentos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcDocumento.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "expediente" in request.form:
        if request.form["expediente"].isnumeric():
            consulta = consulta.filter(ArcDocumento.expediente.contains(request.form["expediente"]))
        else:
            consulta = consulta.filter(ArcDocumento.expediente.contains(safe_expediente(request.form["expediente"])))
    if "partes" in request.form:
        consulta = consulta.filter(or_(ArcDocumento.actor.contains(safe_string(request.form["partes"], save_enie=True)), ArcDocumento.demandado.contains(safe_string(request.form["partes"], save_enie=True))))
    if "tipo" in request.form:
        consulta = consulta.filter_by(tipo=request.form["tipo"])
    if "ubicacion" in request.form:
        consulta = consulta.filter_by(ubicacion=request.form["ubicacion"])
    if "juzgado_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    registros = consulta.order_by(ArcDocumento.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "expediente": {
                    "expediente": resultado.expediente,
                    "url": url_for("arc_documentos.detail", documento_id=resultado.id),
                },
                "juzgado": {
                    "clave": resultado.autoridad.clave,
                    "nombre": resultado.autoridad.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                },
                "anio": resultado.anio,
                "tipo": resultado.tipo,
                "fojas": resultado.fojas,
                "actor": resultado.actor,
                "demandado": resultado.demandado,
                "ubicacion": resultado.ubicacion,
                "partes": {
                    "actor": resultado.actor,
                    "demandado": resultado.demandado,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_documentos.route("/arc_documentos")
def list_active():
    """Listado de Documentos activos"""

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()

    if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles or ROL_ARCHIVISTA in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
        return render_template(
            "arc_documentos/list_admin.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Expedientes",
            estatus="A",
            tipos=ArcDocumento.TIPOS,
            ubicaciones=ArcDocumento.UBICACIONES,
        )

    return render_template(
        "arc_documentos/list.jinja2",
        filtros=json.dumps({"estatus": "A", "juzgado_id": current_user.autoridad.id}),
        titulo="Expedientes",
        estatus="A",
        tipos=ArcDocumento.TIPOS,
        ubicaciones=ArcDocumento.UBICACIONES,
    )


@arc_documentos.route("/arc_documentos/<int:documento_id>")
def detail(documento_id):
    """Detalle de un Documento"""
    documento = ArcDocumento.query.get_or_404(documento_id)

    # mostrar secciones según el ROL
    mostrar_secciones = {}
    current_user_roles = current_user.get_roles()
    if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles or ROL_SOLICITANTE in current_user_roles:
        mostrar_secciones["boton_editar"] = True

    return render_template(
        "arc_documentos/detail.jinja2",
        documento=documento,
        acciones=ArcDocumentoBitacora.ACCIONES,
        mostrar_secciones=mostrar_secciones,
    )


@arc_documentos.route("/arc_documentos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Documento"""
    mostrar_secciones = {}
    current_user_roles = current_user.get_roles()
    if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
        form = ArcDocumentoNewArchivoForm()
        mostrar_secciones["select_juzgado"] = True
    elif ROL_SOLICITANTE in current_user_roles:
        form = ArcDocumentoNewSolicitanteForm()
    else:
        flash("No tiene el ROL para realizar está acción.", "warning")
        return redirect(url_for("arc_documentos.list_active"))
    # Recepción del Formulario
    if form.validate_on_submit():
        # Validar que la clave no se repita
        try:
            num_expediente = safe_expediente(form.num_expediente.data)
        except ValueError:
            num_expediente = None
        if isinstance(form, ArcDocumentoNewArchivoForm):
            juzgado_id = int(form.juzgado_id.data)
            ubicacion = safe_string(form.ubicacion.data)
        else:
            juzgado_id = current_user.autoridad.id
            ubicacion = "JUZGADO"
        anio = int(form.anio.data)
        if ArcDocumento.query.filter_by(expediente=num_expediente).filter_by(autoridad_id=juzgado_id).first():
            flash("El número de expediente ya está en uso para este juzgado. Debe de ser único.", "warning")
        elif anio < 1950 or anio > date.today().year:
            flash(f"El Año debe ser una fecha entre 1950 y el año actual {date.today().year}", "warning")
        elif num_expediente is None:
            flash("El número de expediente no es válido", "warning")
        else:

            documento = ArcDocumento(
                autoridad_id=juzgado_id,
                expediente=num_expediente,
                anio=anio,
                actor=safe_string(form.actor.data, save_enie=True),
                demandado=safe_string(form.demandado.data, save_enie=True),
                juicio=safe_string(form.juicio.data, save_enie=True),
                tipo_juzgado=safe_string(form.tipo_juzgado.data),
                arc_juzgado_origen=form.juzgado_origen.data,
                tipo=safe_string(form.tipo.data),
                fojas=int(form.fojas.data),
                ubicacion=ubicacion,
            )
            documento.save()
            documento_bitacora = ArcDocumentoBitacora(
                arc_documento_id=documento.id,
                usuario=current_user,
                fojas=int(form.fojas.data),
                observaciones=safe_message(form.observaciones.data, max_len=256),
                accion="ALTA",
            )
            documento_bitacora.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Alta de Documento {documento.id}"),
                url=url_for("arc_documentos.detail", documento_id=documento.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Bloquear campos según el ROL
    if ROL_SOLICITANTE in current_user_roles:
        form.juzgado_readonly.data = f"{current_user.autoridad.clave} : {current_user.autoridad.descripcion_corta}"
        form.ubicacion_readonly.data = "JUZGADO"
    return render_template("arc_documentos/new.jinja2", form=form, mostrar_secciones=mostrar_secciones)


@arc_documentos.route("/arc_documentos/edicion/<int:arc_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(arc_documento_id):
    """Editar Documento"""
    documento = ArcDocumento.query.get_or_404(arc_documento_id)
    current_user_roles = current_user.get_roles()
    if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO):
        form = ArcDocumentoEditArchivoForm()
    elif ROL_SOLICITANTE in current_user_roles:
        form = ArcDocumentoEditSolicitanteForm()
    else:
        flash("No tiene el ROL para realizar está acción.", "warning")
        return redirect(url_for("arc_documentos.list_active"))
    # Recepción del Formulario
    if form.validate_on_submit():
        # Validar que la clave no se repita
        try:
            num_expediente = safe_expediente(form.num_expediente.data)
        except ValueError:
            num_expediente = None
        if isinstance(form, ArcDocumentoEditArchivoForm):
            juzgado_id = int(form.juzgado_id.data)
            ubicacion = safe_string(form.ubicacion.data)
            fojas = int(form.fojas.data)
        else:
            juzgado_id = current_user.autoridad.id
            ubicacion = documento.ubicacion
            fojas = documento.fojas
        anio = int(form.anio.data)
        motivo = safe_message(form.observaciones.data, max_len=256)
        if ArcDocumento.query.filter_by(expediente=num_expediente).filter_by(autoridad_id=juzgado_id).filter(ArcDocumento.id != arc_documento_id).first():
            flash("El número de expediente ya está en uso para este juzgado. Debe de ser único.", "warning")
        elif anio < 1950 or anio > date.today().year:
            flash(f"El Año debe ser una fecha entre 1950 y el año actual {date.today().year}", "warning")
        elif num_expediente is None:
            flash("El número de expediente no es válido", "warning")
        else:

            documento.autoridad_id = juzgado_id
            documento.expediente = safe_expediente(num_expediente)
            documento.anio = int(anio)
            documento.actor = safe_string(form.actor.data, save_enie=True)
            documento.demandado = safe_string(form.demandado.data, save_enie=True)
            documento.juicio = safe_string(form.juicio.data, save_enie=True)
            documento.tipo_juzgado = safe_string(form.tipo_juzgado.data)
            documento.arc_juzgado_origen = form.juzgado_origen.data
            documento.tipo = safe_string(form.tipo.data)
            documento.fojas = fojas
            documento.ubicacion = ubicacion
            documento_bitacora = ArcDocumentoBitacora(
                arc_documento_id=documento.id,
                usuario=current_user,
                fojas=fojas,
                observaciones=motivo,
                accion="EDICION DOC",
            )
            documento_bitacora.save()
            documento.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Edición de Documento {documento.id}"),
                url=url_for("arc_documentos.detail", documento_id=documento.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.num_expediente.data = documento.expediente
    form.anio.data = documento.anio
    form.actor.data = documento.actor
    form.demandado.data = documento.demandado
    form.juzgado_origen.data = documento.arc_juzgado_origen
    form.juicio.data = documento.juicio
    form.tipo_juzgado.data = documento.tipo_juzgado
    form.tipo.data = documento.tipo
    if isinstance(form, ArcDocumentoEditArchivoForm):
        form.juzgado_id.data = documento.autoridad_id
        form.ubicacion.data = documento.ubicacion
        form.fojas.data = documento.fojas
    else:
        form.juzgado_readonly.data = f"{current_user.autoridad.clave} : {current_user.autoridad.descripcion_corta}"
        form.ubicacion_readonly.data = documento.ubicacion
        form.fojas_readonly.data = documento.fojas
    return render_template("arc_documentos/edit.jinja2", form=form, documento=documento)


@arc_documentos.route("/arc_documentos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Documento dentro de Expediente Virtual API"""
    num_expediente = ""
    mostrar_secciones = {}
    current_user_roles = current_user.get_roles()
    if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
        form = ArcDocumentoNewArchivoForm()
        mostrar_secciones["select_juzgado"] = True
    elif ROL_SOLICITANTE in current_user_roles:
        form = ArcDocumentoNewSolicitanteForm()
    else:
        flash("No tiene el ROL para realizar está acción.", "warning")
        return redirect(url_for("arc_documentos.list_active"))
    # Proceso de búsqueda
    if "num_expediente" in request.form:
        num_expediente = request.form["num_expediente"]
        load_dotenv()
        EXPEDIENTE_VIRTUAL_API_URL = os.environ.get("EXPEDIENTE_VIRTUAL_API_URL", "")
        if EXPEDIENTE_VIRTUAL_API_URL == "":
            flash("No se declaro la variable de entorno EXPEDIENTE_VIRTUAL_API_URL", "warning")
            return redirect(url_for("arc_documentos.new"))
        EXPEDIENTE_VIRTUAL_API_KEY = os.environ.get("EXPEDIENTE_VIRTUAL_API_KEY", "")
        if EXPEDIENTE_VIRTUAL_API_KEY == "":
            flash("No se declaro la variable de entorno EXPEDIENTE_VIRTUAL_API_KEY", "warning")
            return redirect(url_for("arc_documentos.new"))
        if "/" not in num_expediente or len(num_expediente) < 6:
            flash("Número de Expediente NO válido", "warning")
            return redirect(url_for("arc_documentos.new"))
        autoridad_id = 0
        num_consecutivo, anio = num_expediente.split("/")
        if ROL_SOLICITANTE in current_user_roles:
            autoridad_id = current_user.autoridad.id
        elif ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
            if "juzgadoInput_buscar" not in request.form:
                flash("Necesita indicar un Juzgado en el formulario de búsqueda ", "warning")
                autoridad_id = 0
            else:
                autoridad_id = int(request.form["juzgadoInput_buscar"])
                mostrar_secciones["juzgado_id"] = autoridad_id
        if autoridad_id > 0:
            autoridad = Autoridad.query.get_or_404(autoridad_id)
            juzgado_id = autoridad.datawarehouse_id
            if juzgado_id:
                url_api = f"{EXPEDIENTE_VIRTUAL_API_URL}?apiFunctionName=InfoExpediente&apiParamConsecutivo={num_consecutivo}&apiParamAnio={anio}&apiParamidJuzgado={juzgado_id}&apiKey={EXPEDIENTE_VIRTUAL_API_KEY}"
                # Hace el llamado a la API
                respuesta_api = {}
                try:
                    response = requests.request("GET", url_api, timeout=32)
                    respuesta_api = json.loads(response.text)
                except requests.exceptions.RequestException as err:
                    flash(f"Error en API {err}", "danger")
                    respuesta_api["success"] = None
                    respuesta_api["response"] = "ERROR DE API"
                    respuesta_api["Description"] = "No hubo comunicación con la API"
                if respuesta_api["success"]:
                    if respuesta_api["success"] == "1":
                        flash("Registro encontrado en Expediente Virtual", "success")
                        form.num_expediente.data = num_expediente
                        form.anio.data = anio
                        form.juicio.data = respuesta_api["Juicio"]
                        form.actor.data = respuesta_api["Actor"]
                        form.demandado.data = respuesta_api["Demandado"]
                        form.tipo.data = "EXPEDIENTE"
                        if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
                            form.juzgado_id.data = autoridad_id
                            mostrar_secciones["juzgado_nombre"] = autoridad.nombre
                    else:
                        # Si no encontró nada en Expediente Virtual ahora buscar en SIBED
                        PEGASO_API_URL = os.environ.get("PEGASO_API_URL", "")
                        if PEGASO_API_URL == "":
                            flash("No se declaro la variable de entorno PEGASO_API_URL", "warning")
                            return redirect(url_for("arc_documentos.new"))
                        PEGASO_API_KEY = os.environ.get("PEGASO_API_KEY", "")
                        if PEGASO_API_KEY == "":
                            flash("No se declaro la variable de entorno PEGASO_API_KEY", "warning")
                            return redirect(url_for("arc_documentos.new"))
                        headers = {"Accept": "application/json", "X-Api-Key": PEGASO_API_KEY}
                        url_api = f"{PEGASO_API_URL}?juzgado_id={autoridad_id}&num_expediente{num_expediente}"
                        # Hace el llamado a la API
                        respuesta_api = {}
                        try:
                            response = requests.request("GET", url=url_api, headers=headers, timeout=32)
                            respuesta_api = json.loads(response.text)
                        except requests.exceptions.RequestException as err:
                            flash(f"Error en API {err}", "danger")
                            respuesta_api["success"] = None
                            respuesta_api["response"] = "ERROR DE API"
                            respuesta_api["Description"] = "No hubo comunicación con la API"

                        if "success" in respuesta_api:
                            if respuesta_api["success"]:
                                flash("Registro encontrado en SIBED", "success")
                                form.num_expediente.data = num_expediente
                                form.anio.data = anio
                                form.juicio.data = respuesta_api["juicio"]
                                form.actor.data = respuesta_api["actor"]
                                form.demandado.data = respuesta_api["demandado"]
                                form.tipo.data = respuesta_api["tipo"]
                                if respuesta_api["juzgado_origen_id"] is None:
                                    form.juzgado_origen.data = ""
                                else:
                                    form.juzgado_origen.data = respuesta_api["juzgado_origen_id"]
                                if respuesta_api["fojas"] is None:
                                    form.fojas.data = ""
                                else:
                                    form.fojas.data = respuesta_api["fojas"]
                                if respuesta_api["observaciones"] is None:
                                    form.observaciones.data = ""
                                else:
                                    form.observaciones.data = respuesta_api["observaciones"]
                                if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
                                    form.juzgado_id.data = autoridad_id
                                    mostrar_secciones["juzgado_nombre"] = autoridad.nombre
                            else:
                                flash("Registro NO encontrado", "warning")
                                if ROL_JEFE_REMESA in current_user_roles or current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles:
                                    mostrar_secciones["juzgado_nombre"] = autoridad.nombre
                        else:
                            flash(f"Error en API {response.text}", "danger")
                else:
                    flash(f"{respuesta_api['response']}: {respuesta_api['Description']}", "danger")
            else:
                flash("No tiene una autoridad asignada compatible con el campo datawarehouse_id", "warning")
    # Bloquear campos según el ROL
    if ROL_SOLICITANTE in current_user_roles:
        form.juzgado_readonly.data = f"{current_user.autoridad.clave} : {current_user.autoridad.descripcion_corta}"
        form.ubicacion_readonly.data = "JUZGADO"
    elif ROL_JEFE_REMESA in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
        mostrar_secciones["select_juzgado"] = True
    return render_template("arc_documentos/new.jinja2", form=form, num_expediente=num_expediente, mostrar_secciones=mostrar_secciones)
