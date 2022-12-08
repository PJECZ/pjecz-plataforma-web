"""
Archivo Documentos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_expediente, safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.arc_documentos.forms import ArcDocumentoNewForm, ArcDocumentoEditForm

MODULO = "ARC DOCUMENTOS"

# Roles necesarios
ROL_JEFE_REMESA = "ARCHIVO JEFE REMESA"
ROL_ARCHIVISTA = "ARCHIVO ARCHIVISTA"
ROL_SOLICITANTE = "ARCHIVO SOLICITANTE"

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

    if current_user.can_admin(MODULO):
        return render_template(
            "arc_documentos/list_admin.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Documentos",
            estatus="A",
            tipos=ArcDocumento.TIPOS,
            ubicaciones=ArcDocumento.UBICACIONES,
        )

    return render_template(
        "arc_documentos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Documentos",
        estatus="A",
        tipos=ArcDocumento.TIPOS,
        ubicaciones=ArcDocumento.UBICACIONES,
    )


@arc_documentos.route("/arc_documentos/<int:documento_id>")
def detail(documento_id):
    """Detalle de un Documento"""
    documento = ArcDocumento.query.get_or_404(documento_id)
    return render_template("arc_documentos/detail.jinja2", documento=documento, acciones=ArcDocumentoBitacora.ACCIONES)


@arc_documentos.route("/arc_documentos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Documento"""
    form = ArcDocumentoNewForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        try:
            num_expediente = safe_expediente(form.num_expediente.data)
        except ValueError:
            num_expediente = None
        juzgado_id = int(form.juzgado_id.data)
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
                expediente_reasignado=safe_expediente(form.num_expediente_reasignado.data),
                juzgado_reasignado=safe_string(form.juzgado_reasignado.data, save_enie=True),
                tipo=safe_string(form.tipo.data),
                ubicacion=safe_string(form.ubicacion.data),
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
    return render_template("arc_documentos/new.jinja2", form=form)


@arc_documentos.route("/arc_documentos/edicion/<int:arc_documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(arc_documento_id):
    """Editar Documento"""
    documento = ArcDocumento.query.get_or_404(arc_documento_id)
    form = ArcDocumentoEditForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        try:
            num_expediente = safe_expediente(form.num_expediente.data)
        except ValueError:
            num_expediente = None
        juzgado_id = int(form.juzgado_id.data)
        anio = int(form.anio.data)
        motivo = safe_message(form.observaciones.data, max_len=256)
        if ArcDocumento.query.filter_by(expediente=num_expediente).filter_by(autoridad_id=juzgado_id).filter(ArcDocumento.id != arc_documento_id).first():
            flash("El número de expediente ya está en uso para este juzgado. Debe de ser único.", "warning")
        elif anio < 1950 or anio > date.today().year:
            flash(f"El Año debe ser una fecha entre 1950 y el año actual {date.today().year}", "warning")
        elif num_expediente is None:
            flash("El número de expediente no es válido", "warning")
        elif motivo is None or len(motivo) < 10:
            flash("Escriba un motivo más descriptivo", "warning")
        else:
            documento.autoridad_id = juzgado_id
            documento.expediente = num_expediente
            documento.anio = anio
            documento.actor = safe_string(form.actor.data, save_enie=True)
            documento.demandado = safe_string(form.demandado.data, save_enie=True)
            documento.juicio = safe_string(form.juicio.data, save_enie=True)
            documento.tipo_juzgado = safe_string(form.tipo_juzgado.data)
            documento.expediente_reasignado = safe_expediente(form.num_expediente_reasignado.data)
            documento.juzgado_reasignado = safe_string(form.juzgado_reasignado.data, save_enie=True)
            documento.tipo = safe_string(form.tipo.data)
            documento.ubicacion = safe_string(form.ubicacion.data)
            documento.save()
            documento_bitacora = ArcDocumentoBitacora(
                arc_documento_id=documento.id,
                usuario=current_user,
                observaciones=motivo,
                accion="EDICION DOC",
            )
            documento_bitacora.save()
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
    form.juzgado_id.data = documento.autoridad_id
    form.actor.data = documento.actor
    form.demandado.data = documento.demandado
    form.juicio.data = documento.juicio
    form.tipo_juzgado.data = documento.tipo_juzgado
    form.num_expediente_reasignado.data = documento.expediente_reasignado
    form.tipo.data = documento.tipo
    form.ubicacion.data = documento.ubicacion
    return render_template("arc_documentos/edit.jinja2", form=form, documento=documento)
