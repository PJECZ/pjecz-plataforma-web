"""
Archivo Remesa Documentos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, text
from sqlalchemy.sql.expression import delete
from plataforma_web.extensions import db

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_juzgados_extintos.models import ArcJuzgadoExtinto
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.arc_remesas_documentos.forms import ArcRemesaDocumentoEditForm, ArcRemesaDocumentoArchiveForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE, ROL_RECEPCIONISTA

MODULO = "ARC REMESAS"

arc_remesas_documentos = Blueprint("arc_remesas_documentos", __name__, template_folder="templates")


@arc_remesas_documentos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_remesas_documentos.route("/arc_remesas_documentos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Documentos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcRemesaDocumento.query.join(ArcDocumento)
    if "id" in request.form:
        consulta = consulta.filter(ArcRemesaDocumento.id == request.form["id"])
    if "expediente" in request.form:
        consulta = consulta.filter(ArcDocumento.expediente.contains(request.form["expediente"]))
    if "estatus" in request.form:
        consulta = consulta.filter(ArcRemesaDocumento.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(ArcRemesaDocumento.estatus == "A")
    if "remesa_id" in request.form:
        consulta = consulta.filter(ArcRemesaDocumento.arc_remesa_id == request.form["remesa_id"])

    # Ordena los registros resultantes por fecha y número de expediente
    registros = consulta.order_by(ArcDocumento.anio.desc()).order_by(ArcDocumento.expediente_numero.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=resultado.id),
                },
                "expediente": {
                    "expediente": resultado.arc_documento.expediente,
                    "url": url_for("arc_documentos.detail", documento_id=resultado.arc_documento.id),
                },
                "anio": resultado.arc_documento.anio,
                "tipo": resultado.arc_documento.arc_documento_tipo.nombre,
                "juicio": resultado.arc_documento.juicio,
                "juzgado_origen": {
                    "clave": resultado.arc_documento.arc_juzgado_origen.clave if resultado.arc_documento.arc_juzgado_origen_id is not None else "",
                    "nombre": resultado.arc_documento.arc_juzgado_origen.descripcion_corta if resultado.arc_documento.arc_juzgado_origen_id is not None else "",
                },
                "fojas": {
                    "nuevas": resultado.fojas,
                    "anteriores": resultado.arc_documento.fojas,
                },
                "actor": resultado.arc_documento.actor,
                "demandado": resultado.arc_documento.demandado,
                "partes": {
                    "actor": resultado.arc_documento.actor,
                    "demandado": resultado.arc_documento.demandado,
                },
                "observaciones_solicitante": resultado.observaciones_solicitante if resultado.observaciones_solicitante else "",
                "observaciones_archivista": resultado.observaciones_archivista if resultado.observaciones_archivista else "",
                "ubicacion": resultado.arc_documento.ubicacion,
                "anomalia": resultado.anomalia,
                "acciones": {
                    "ver": url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=resultado.id),
                    "editar": url_for("arc_remesas_documentos.edit", arc_remesa_documento_id=resultado.id),
                    "eliminar": url_for("arc_remesas_documentos.delete", arc_remesa_documento_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_remesas_documentos.route("/arc_remesas_documentos/detalle/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def detail(arc_remesa_documento_id):
    """Detalle de un documento anexo de una Remesa"""

    # Localizamos el documento anexo de la remesa
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)

    # Mostramos diferentes secciones dependiendo del ROL
    current_user_roles = current_user.get_roles()
    mostrar_secciones = {}
    if ROL_ARCHIVISTA in current_user_roles or current_user.can_admin(MODULO):
        mostrar_secciones["estado_actual"] = False
        mostrar_secciones["observaciones_archivista"] = False
        remesa = ArcRemesa.query.get_or_404(remesa_documento.arc_remesa_id)
        if remesa.estado == "ASIGNADO":
            mostrar_secciones["archivar"] = True
            form = ArcRemesaDocumentoArchiveForm()
            form.fojas.data = remesa_documento.fojas
            if remesa_documento.anomalia is not None:
                form.anomalia.data = remesa_documento.anomalia
                form.observaciones_archivista.data = remesa_documento.observaciones_archivista
                if remesa_documento.arc_documento.ubicacion == "ARCHIVO":
                    mostrar_secciones["estado_actual"] = "ARCHIVADO CON ANOMALÍA"
                else:
                    mostrar_secciones["estado_actual"] = "RECHAZADO"
            else:
                if remesa_documento.arc_documento.ubicacion == "ARCHIVO":
                    mostrar_secciones["estado_actual"] = "ARCHIVADO"
            # Mostrar el template resultante
            return render_template(
                "arc_remesas_documentos/detail.jinja2",
                remesa=remesa_documento.arc_remesa,
                documento=remesa_documento.arc_documento,
                arc_remesa_documento=remesa_documento,
                mostrar_secciones=mostrar_secciones,
                form=form,
            )

    # Mostrar el template resultante
    return render_template(
        "arc_remesas_documentos/detail.jinja2",
        remesa=remesa_documento.arc_remesa,
        documento=remesa_documento.arc_documento,
        arc_remesa_documento=remesa_documento,
        mostrar_secciones=mostrar_secciones,
    )


@arc_remesas_documentos.route("/arc_remesas_documentos/editar/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(arc_remesa_documento_id):
    """Editar un documento anexo de una Remesa"""
    # TODO: Separar la edición por parte del Solicitante y por Archivo

    # Localizamos el documento anexo de la remesa
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)

    # Formulario de Edición
    form = ArcRemesaDocumentoEditForm()
    if form.validate_on_submit():
        remesa_documento.fojas = int(form.fojas.data)
        remesa_documento.tipo_juzgado = safe_string(form.tipo_juzgado.data)
        remesa_documento.observaciones_solicitante = safe_message(form.observaciones_solicitante.data, default_output_str=None)
        remesa_documento.save()
        flash(f"Documento Anexo [{remesa_documento.arc_documento.expediente}] editado correctamente.", "success")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))

    # Pre-cargar de datos al formulario de edición
    form.fojas.data = remesa_documento.fojas
    form.tipo_juzgado.data = remesa_documento.tipo_juzgado
    form.observaciones_solicitante.data = remesa_documento.observaciones_solicitante

    # Mostrar el template resultante
    return render_template("arc_remesas_documentos/edit.jinja2", remesa=remesa_documento.arc_remesa, documento=remesa_documento.arc_documento, arc_remesa_documento=remesa_documento, form=form)


@arc_remesas_documentos.route("/arc_remesas_documentos/eliminar/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(arc_remesa_documento_id):
    """Quitar un documento anexo de una Remesa"""

    # Localizamos el documento anexo de la remesa
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)

    # Datos temporales para consultar después de la eliminación
    expediente = remesa_documento.arc_documento.expediente
    remesa_id = remesa_documento.arc_remesa_id
    remesa = ArcRemesa.query.get_or_404(remesa_id)

    # Validamos los roles permitidos para esta acción
    current_user_roles = current_user.get_roles()
    if not (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles):
        flash("Solo el ROL de SOLICITANTE puede quitar anexos de una remesa.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Elimina permanentemente el registro de documento anexo a esta remesa.
    sql = text(f"DELETE FROM {ArcRemesaDocumento.__tablename__} WHERE id = {arc_remesa_documento_id};")
    db.engine.execute(sql)
    # Actualizar el número de documentos anexos de la remesa
    remesa.num_documentos = ArcRemesaDocumento.query.filter_by(arc_remesa=remesa).count()
    remesa.save()

    # Mostramos el resultado obtenido
    flash(f"Documento Anexo [{expediente}] extraído de la lista de anexos correctamente.", "success")
    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))


@arc_remesas_documentos.route("/arc_remesas_documentos/archivar/<int:arc_remesa_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def archive(arc_remesa_documento_id):
    """Archivar un documento anexo de una Remesa"""

    # Localizamos el documento anexo de la remesa
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)

    # Validamos los roles permitidos para esta acción
    current_user_roles = current_user.get_roles()
    if not (ROL_ARCHIVISTA in current_user_roles or current_user.can_admin(MODULO)):
        flash("Solo el ROL de ARCHIVISTA puede archivar anexos de una remesa.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))

    # Leemos el Formulario
    form = ArcRemesaDocumentoArchiveForm()
    if form.validate_on_submit():
        documento = ArcDocumento.query.get_or_404(remesa_documento.arc_documento_id)
        if documento.estatus != "A":
            flash("El documento se encuentra eliminado.", "warning")
            return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))

        # Identificamos la acción a realizar dependiendo del botón presionado en el formulario
        if "archivar" in request.form:
            if request.form["archivar"] == "Archivar":
                if not "fojas" in request.form or request.form["fojas"] == "":
                    flash("Para ARCHIVAR necesita indicar el número de fojas", "warning")
                    return redirect(url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=arc_remesa_documento_id))
                # Guardamos las observaciones del Archivista sobre el anexo
                remesa_documento.observaciones_archivista = safe_message(form.observaciones_archivista.data, default_output_str=None)
                remesa_documento.anomalia = None
                remesa_documento.save()
                # Guardamos cambios del documento
                documento.fojas = int(form.fojas.data)
                documento.ubicacion = "ARCHIVO"
                documento.save()
                # Añadir acción a la bitácora del documento
                documento_bitacora = ArcDocumentoBitacora(
                    arc_documento=documento,
                    usuario=current_user,
                    fojas=int(form.fojas.data),
                    observaciones=safe_message(form.observaciones_archivista.data, default_output_str=None),
                    accion="ARCHIVAR",
                )
                documento_bitacora.save()
                # Añadir acción a la bitácora del sistema
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Documento {documento.id} Archivado."),
                    url=url_for("arc_archivos.list_active"),
                )
                bitacora.save()
                # Actualizamos el número de anomalías registradas en la remesa padre
                remesa = ArcRemesa.query.get_or_404(remesa_documento.arc_remesa_id)
                num_anomalias = ArcRemesaDocumento.query.filter_by(arc_remesa=remesa).filter(ArcRemesaDocumento.anomalia != None).count()
                remesa.num_anomalias = num_anomalias
                remesa.save()

                flash("El documento anexo ha sido ARCHIVADO con éxito.", "success")
            elif request.form["archivar"] == "Rechazar":
                if not "anomalia" in request.form or request.form["anomalia"] == "":
                    flash("Para RECHAZAR necesita indicar una anomalía", "warning")
                    return redirect(url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=arc_remesa_documento_id))
                # Guardamos las observaciones del Archivista sobre el anexo
                remesa_documento.observaciones_archivista = safe_message(form.observaciones_archivista.data, default_output_str=None)
                remesa_documento.anomalia = safe_string(form.anomalia.data)
                remesa_documento.save()
                # Guardamos cambios del documento
                documento.ubicacion = "JUZGADO"
                documento.save()
                # Añadir acción a la bitácora del documento
                documento_bitacora = ArcDocumentoBitacora(
                    arc_documento=documento,
                    usuario=current_user,
                    observaciones=safe_message(f"ANOMALÍA: {remesa_documento.anomalia}. NOTA: {remesa_documento.observaciones_archivista}", default_output_str=None),
                    accion="ANOMALIA",
                )
                documento_bitacora.save()
                # Añadir acción a la bitácora del sistema
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Documento {documento.id} Rechazado."),
                    url=url_for("arc_archivos.list_active"),
                )
                bitacora.save()
                # Actualizamos el número de anomalías registradas en la remesa padre
                remesa = ArcRemesa.query.get_or_404(remesa_documento.arc_remesa_id)
                num_anomalias = ArcRemesaDocumento.query.filter_by(arc_remesa=remesa).filter(ArcRemesaDocumento.anomalia != None).count()
                remesa.num_anomalias = num_anomalias
                remesa.save()

                flash("El documento anexo ha sido RECHAZADO con éxito.", "success")
            elif request.form["archivar"] == "Archivar con Anomalía":
                if not "fojas" in request.form or request.form["fojas"] == "" or not "anomalia" in request.form or request.form["anomalia"] == "":
                    flash("Para ARCHIVAR CON ANOMALÍA necesita indicar un número de fojas y una anomalía", "warning")
                    return redirect(url_for("arc_remesas_documentos.detail", arc_remesa_documento_id=arc_remesa_documento_id))
                # Guardamos las observaciones del Archivista sobre el anexo
                remesa_documento.observaciones_archivista = safe_message(form.observaciones_archivista.data, default_output_str=None)
                remesa_documento.anomalia = safe_string(form.anomalia.data)
                remesa_documento.save()
                # Guardamos cambios del documento
                documento.fojas = int(form.fojas.data)
                documento.ubicacion = "ARCHIVO"
                documento.save()
                # Añadir acción a la bitácora del documento
                documento_bitacora = ArcDocumentoBitacora(
                    arc_documento=documento,
                    usuario=current_user,
                    fojas=int(form.fojas.data),
                    observaciones=safe_message(f"ANOMALÍA: {remesa_documento.anomalia}. NOTA: {remesa_documento.observaciones_archivista}", default_output_str=None),
                    accion="ARCHIVAR",
                )
                documento_bitacora.save()
                # Añadir acción a la bitácora del sistema
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Documento {documento.id} Archivado con Anomalía."),
                    url=url_for("arc_archivos.list_active"),
                )
                bitacora.save()
                # Actualizamos el número de anomalías registradas en la remesa padre
                remesa = ArcRemesa.query.get_or_404(remesa_documento.arc_remesa_id)
                num_anomalias = ArcRemesaDocumento.query.filter_by(arc_remesa=remesa).filter(ArcRemesaDocumento.anomalia != None).count()
                remesa.num_anomalias = num_anomalias
                remesa.save()

                flash("El documento anexo ha sido ARCHIVADO CON ANOMALÍA con éxito.", "success")
            else:
                flash(f"No se reconoce la acción '{request.form['archivar']}'.", "warning")
        else:
            flash("Acción desconocida", "warning")
    else:
        flash("La operación de ARCHIVAR NO se completo.", "danger")

    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))


@arc_remesas_documentos.route("/arc_remesas_documentos/imprimir_listado/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def print_list(remesa_id):
    """Envía a la hoja de impresión de listado de documentos anexos a una Remesa"""

    # Localizar remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)

    # Extremos el listado de documentos anexos de la remesa
    documentos_anexos = ArcRemesaDocumento.query.filter_by(arc_remesa_id=remesa_id).filter_by(estatus="A")
    documentos_anexos = documentos_anexos.join(ArcDocumento)
    documentos_anexos = documentos_anexos.order_by(ArcDocumento.anio.desc()).order_by(ArcDocumento.expediente_numero.desc()).all()

    # Resultado final de éxito
    return render_template("arc_remesas_documentos/print_list.jinja2", remesa=remesa, documentos_anexos=documentos_anexos)
