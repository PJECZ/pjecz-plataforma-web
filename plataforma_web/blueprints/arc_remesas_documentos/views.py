"""
Archivo Remesa Documentos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.arc_remesas_documentos.forms import ArcRemesaDocumentoEditForm, ArcRemesaDocumentoArchiveForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE

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
    consulta = ArcRemesaDocumento.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "remesa_id" in request.form:
        consulta = consulta.filter_by(arc_remesa_id=request.form["remesa_id"])

    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    registros = consulta.order_by(ArcRemesaDocumento.id.desc()).offset(start).limit(rows_per_page).all()
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
                "tipo": resultado.arc_documento.tipo,
                "juicio": resultado.arc_documento.juicio,
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
                "observaciones": resultado.observaciones,
                "ubicacion": resultado.arc_documento.ubicacion,
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
        if remesa_documento.arc_documento.ubicacion == "REMESA":
            mostrar_secciones["archivar"] = True
            form = ArcRemesaDocumentoArchiveForm()
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

    # Localizamos el documento anexo de la remesa
    remesa_documento = ArcRemesaDocumento.query.get_or_404(arc_remesa_documento_id)

    # Formulario de Edición
    form = ArcRemesaDocumentoEditForm()
    if form.validate_on_submit():
        remesa_documento.fojas = int(form.fojas.data)
        remesa_documento.tipo = safe_string(form.tipo.data)
        remesa_documento.observaciones = safe_message(form.observaciones.data)
        remesa_documento.tiene_anomalia = form.tiene_anomalia.data
        remesa_documento.save()
        flash(f"Documento Anexo [{remesa_documento.arc_documento.expediente}] editado correctamente.", "success")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))

    # Pre-cargar de datos al formulario de edición
    form.fojas.data = remesa_documento.fojas
    form.tipo.data = remesa_documento.tipo
    form.observaciones.data = remesa_documento.observaciones
    form.tiene_anomalia.data = remesa_documento.tiene_anomalia

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

    # Validamos los roles permitidos para esta acción
    current_user_roles = current_user.get_roles()
    if ROL_SOLICITANTE not in current_user_roles or not current_user.can_admin(MODULO):
        flash("Solo el ROL de SOLICITANTE puede quitar anexos de una remesa.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Elimina permanentemente el registro de documento anexo a esta remesa.
    remesa_documento.delete(permanently=True)

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
        elif documento.ubicacion != "REMESA":
            flash("El documento debe estar ubicado en REMESA.", "warning")
            return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))

        # Guardamos las observaciones del Archivista sobre el anexo
        remesa_documento.observaciones = safe_message(form.observaciones.data)
        remesa_documento.save()
        # Guardamos cambios en el documento
        documento.fojas = int(form.fojas.data)
        documento.ubicacion = "ARCHIVO"
        documento.save()
        # Guardamos operación en la operación de la bitácora del documento
        documento_bitacora = ArcDocumentoBitacora(
            arc_documento=documento,
            usuario=current_user,
            fojas=int(form.fojas.data),
            observaciones=safe_message(form.observaciones.data),
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
        flash("Documento Anexo ARCHIVADO con éxito.", "success")
    else:
        flash("La operación de ARCHIVAR NO se completo.", "danger")

    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_documento.arc_remesa_id))
