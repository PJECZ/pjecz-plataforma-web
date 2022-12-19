"""
Archivo Documentos Solicitudes, vistas
"""
import json
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_expediente, safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_documentos_solicitudes.models import ArcDocumentoSolicitud
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.blueprints.arc_documentos_solicitudes.forms import ArcDocumentoSolicitudNewForm, ArcDocumentoSolicitudAsignationForm, ArcDocumentoSolicitudFoundForm, ArcDocumentoSolicitudSendForm, ArcDocumentoSolicitudReceiveForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE


MODULO = "ARC DOCUMENTOS SOLICITUDES"


arc_documentos_solicitudes = Blueprint("arc_documentos_solicitudes", __name__, template_folder="templates")


@arc_documentos_solicitudes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Solicitudes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcDocumentoSolicitud.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "juzgado_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    if "asignado_id" in request.form:
        consulta = consulta.filter_by(usuario_asignado_id=int(request.form["asignado_id"]))
    if "arc_documento_id" in request.form:
        consulta = consulta.filter_by(arc_documento_id=int(request.form["arc_documento_id"]))
    if "esta_archivado" in request.form:
        consulta = consulta.filter_by(esta_archivado=bool(request.form["esta_archivado"]))
    if "omitir_cancelados" in request.form:
        consulta = consulta.filter(ArcDocumentoSolicitud.estado != "CANCELADO")
    if "omitir_archivados" in request.form:
        consulta = consulta.filter(ArcDocumentoSolicitud.esta_archivado != True)
    if "mostrar_archivados" in request.form:
        consulta = consulta.filter_by(esta_archivado=True)
    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    if "orden_acendente" in request.form:
        registros = consulta.order_by(ArcDocumentoSolicitud.id.desc()).offset(start).limit(rows_per_page).all()
    else:
        registros = consulta.order_by(ArcDocumentoSolicitud.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "solicitud": {
                    "id": resultado.id,
                    "url": url_for("arc_documentos_solicitudes.detail", solicitud_id=resultado.id),
                },
                "juzgado": {
                    "clave": resultado.autoridad.clave,
                    "nombre": resultado.autoridad.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                },
                "documento": {
                    "expediente": resultado.arc_documento.expediente,
                    "url": url_for("arc_documentos.detail", documento_id=resultado.arc_documento.id),
                },
                "tiempo": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "estado": resultado.estado,
                "tiempo_recepcion": "" if resultado.tiempo_recepcion is None else resultado.tiempo_recepcion.strftime("%Y-%m-%d %H:%M:%S"),
                "asignado": {
                    "nombre": "SIN ASIGNAR" if resultado.usuario_asignado is None else resultado.usuario_asignado.nombre,
                    "url": "" if resultado.usuario_asignado is None else url_for("usuarios.detail", usuario_id=resultado.usuario_asignado.id),
                },
                "num_folio": resultado.num_folio,
                "observaciones_solicitud": resultado.observaciones_solicitud,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/<int:solicitud_id>")
def detail(solicitud_id):
    """Detalle de una Solicitud"""

    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    current_user_roles = current_user.get_roles()
    mostrar_secciones = {
        "boton_cancelar_solicitud": False,
        "boton_pasar_historial": False,
    }
    estado_text = {
        "texto": None,
        "class": None,
    }

    # Sobre-escribir estados dependiendo del ROL
    estados = {
        ROL_SOLICITANTE: {
            "ASIGNADO": {
                "TEXTO": "BUSCANDO",
                "COLOR": "bg-primary",
            },
        },
        ROL_ARCHIVISTA: {
            "ASIGNADO": {
                "TEXTO": "PENDIENTE",
                "COLOR": "bg-warning text-dark",
            },
        },
        "DEFAULT": {
            "SOLICITADO": "bg-warning text-dark",
            "CANCELADO": "bg-secondary",
            "ASIGNADO": "bg-primary",
            "ENCONTRADO": "bg-purple",
            "NO ENCONTRADO": "bg-danger",
            "ENVIANDO": "bg-pink",
            "ENTREGADO": "bg-success",
        },
    }
    # Establece el rol activo
    rol_activo = None
    if ROL_SOLICITANTE in current_user_roles:
        rol_activo = ROL_SOLICITANTE
    elif ROL_JEFE_REMESA in current_user_roles:
        rol_activo = ROL_JEFE_REMESA
    elif ROL_ARCHIVISTA in current_user_roles:
        rol_activo = ROL_ARCHIVISTA

    # Sobre-escribe de ser necesario el texto y color del estado de la solicitud dependiendo del ROL activo
    estado_text["texto"] = solicitud.estado
    estado_text["class"] = None
    if solicitud.estado in estados["DEFAULT"]:
        estado_text["texto"] = solicitud.estado
        estado_text["class"] = estados["DEFAULT"][solicitud.estado]
    if rol_activo in estados:
        if solicitud.estado in estados[rol_activo]:
            if "TEXTO" in estados[rol_activo][solicitud.estado]:
                estado_text["texto"] = estados[rol_activo][solicitud.estado]["TEXTO"]
            if "COLOR" in estados[rol_activo][solicitud.estado]:
                estado_text["class"] = estados[rol_activo][solicitud.estado]["COLOR"]

    # Lógica para mostrar secciones
    if solicitud.estado == "SOLICITADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles):
        mostrar_secciones["boton_cancelar_solicitud"] = True
    if solicitud.estado == "CANCELADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
    if solicitud.estado == "ASIGNADO" and (current_user.can_admin(MODULO) or ROL_ARCHIVISTA in current_user_roles):
        mostrar_secciones["formulario_encontrado"] = True
    if solicitud.estado == "NO ENCONTRADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
    if solicitud.estado == "ENTREGADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
    if solicitud.esta_archivado:
        mostrar_secciones["boton_pasar_historial"] = False

    # Mostrar vista con formulario de asignación
    if solicitud.estado == "SOLICITADO" or solicitud.estado == "ASIGNADO":
        if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles:
            form = ArcDocumentoSolicitudAsignationForm()
            archivistas = Usuario.query.join(UsuarioRol).join(Rol)
            archivistas = archivistas.filter(Rol.nombre == ROL_ARCHIVISTA)
            archivistas = archivistas.filter(UsuarioRol.estatus == "A").filter(Usuario.estatus == "A").filter(Rol.estatus == "A")
            archivistas = archivistas.all()
            return render_template(
                "arc_documentos_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                archivistas=archivistas,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
            )
    if solicitud.estado == "ASIGNADO":
        if current_user.can_admin(MODULO) or ROL_ARCHIVISTA in current_user_roles:
            form = ArcDocumentoSolicitudFoundForm()
            return render_template(
                "arc_documentos_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
            )
    if solicitud.estado == "NO ENCONTRADO":
        return render_template(
            "arc_documentos_solicitudes/detail.jinja2",
            solicitud=solicitud,
            mostrar_secciones=mostrar_secciones,
            estado_text=estado_text,
        )
    if solicitud.estado == "ENCONTRADO":
        if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles:
            form = ArcDocumentoSolicitudSendForm()
            mostrar_secciones["enviar"] = True
            return render_template(
                "arc_documentos_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
            )
    if solicitud.estado == "ENVIANDO":
        if current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles:
            form = ArcDocumentoSolicitudReceiveForm()
            mostrar_secciones["recibir"] = True
            return render_template(
                "arc_documentos_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
            )
    if solicitud.estado == "ENTREGADO":
        mostrar_secciones["entregado"] = True
        return render_template(
            "arc_documentos_solicitudes/detail.jinja2",
            solicitud=solicitud,
            mostrar_secciones=mostrar_secciones,
            estado_text=estado_text,
        )

    # Por defecto mostramos solo los detalles de la solicitud
    return render_template(
        "arc_documentos_solicitudes/detail.jinja2",
        solicitud=solicitud,
        mostrar_secciones=mostrar_secciones,
        estado_text=estado_text,
    )


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/nuevo/<int:documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(documento_id):
    """Nuevo Documento"""
    documento = ArcDocumento.query.get_or_404(documento_id)
    form = ArcDocumentoSolicitudNewForm()
    if form.validate_on_submit():
        if documento.ubicacion != "ARCHIVO":
            flash("El documento solo puede ser solicitado cuando su ubicación está en ARCHIVO.", "warning")
        elif not current_user.can_admin(MODULO) and documento.autoridad != current_user.autoridad:
            flash("Solo se pueden solicitar documentos de la misma Autoridad.", "warning")
        elif ArcDocumentoSolicitud.query.filter_by(arc_documento=documento).filter_by(esta_archivado=False).filter_by(estatus="A").first():
            flash("Este documento ya se encuentra en proceso de solicitud.", "warning")
        else:
            fojas = None
            if form.fojas_nuevas.data is None or form.fojas_nuevas.data == "":
                fojas = None
            else:
                fojas = int(form.fojas_nuevas.data)
            solicitud = ArcDocumentoSolicitud(
                arc_documento=documento,
                autoridad=documento.autoridad,
                usuario_receptor=None,
                tiempo_recepcion=None,
                esta_archivado=False,
                num_folio=safe_string(form.num_folio.data),
                fojas=fojas,
                observaciones_solicitud=safe_message(form.observaciones.data),
                estado="SOLICITADO",
            )
            solicitud.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Solicitud de Documento {solicitud.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.num_expediente.data = documento.expediente
    form.anio.data = documento.anio
    form.actor.data = documento.actor
    form.demandado.data = documento.demandado
    form.juicio.data = documento.juicio
    form.tipo_juzgado.data = documento.tipo_juzgado
    form.tipo.data = documento.tipo
    form.fojas_actuales.data = documento.fojas
    form.ubicacion.data = documento.ubicacion
    return render_template("arc_documentos_solicitudes/new.jinja2", documento_id=documento.id, form=form)


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/asignar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def asign(solicitud_id):
    """Asignar solicitud a Archivista"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    form = ArcDocumentoSolicitudAsignationForm()
    if form.validate_on_submit():
        if solicitud.estado != "SOLICITADO" and solicitud.estado != "ASIGNADO":
            flash("No puede asignar a alguien estando la solicitud en un estado diferente a SOLICITADO o ASIGNADO.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
            flash(f"Solo puede asignar el ROL de {ROL_JEFE_REMESA}.", "warning")
        else:
            if form.asignado.data is None or form.asignado.data == "":
                solicitud.estado = "SOLICITADO"
                solicitud.usuario_asignado = None
            else:
                solicitud.estado = "ASIGNADO"
                solicitud.usuario_asignado_id = int(form.asignado.data)
            solicitud.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Asignación de Archivista a Solicitud {solicitud.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/cancelar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(solicitud_id):
    """Cancelar una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "SOLICITADO":
        flash("No puede cancelar una solicitud en un estado diferente a SOLICITADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede cancelar el ROL de {ROL_SOLICITANTE}.", "warning")
    else:
        solicitud.estado = "CANCELADO"
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Cancelación de Solicitud {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/pasar_historial/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def history(solicitud_id):
    """Pasar al historial una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado not in ["CANCELADO", "NO ENCONTRADO", "ENTREGADO"]:
        flash("No puede pasar al historial una solicitud en este estado.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede pasar al historial el ROL de {ROL_SOLICITANTE}.", "warning")
    else:
        solicitud.esta_archivado = True
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud pasada al Historial {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/encontrado/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def found(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    documento = ArcDocumento.query.get_or_404(solicitud.arc_documento_id)
    if solicitud.estado != "ASIGNADO":
        flash("No puede cambiar el estado a ENCONTRADO de una solicitud que está en un estado diferente a ASIGNADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_ARCHIVISTA not in current_user.get_roles():
        flash(f"Solo puede cambiar el estado a ENCONTRADO el ROL de {ROL_ARCHIVISTA}.", "warning")
    else:
        fojas = None
        if "fojas" in request.form:
            fojas = int(request.form["fojas"])
        solicitud.estado = "ENCONTRADO"
        if documento.fojas != fojas:
            documento.fojas = fojas
        if "fojas" in request.form or "observaciones" in request.form:
            solicitud_bitacora = ArcDocumentoBitacora(
                arc_documento=solicitud.arc_documento,
                usuario=current_user,
                fojas=fojas,
                observaciones=request.form["observaciones"],
                accion="CORRECCION FOJAS",
            )
            solicitud_bitacora.save()
        documento.save()
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud Encontrada {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/no_encontrado/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def no_found(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "ASIGNADO":
        flash("No puede cambiar el estado a NO ENCONTRADO de una solicitud que está en un estado diferente a ASIGNADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_ARCHIVISTA not in current_user.get_roles():
        flash(f"Solo puede cambiar el estado a NO ENCONTRADO el ROL de {ROL_ARCHIVISTA}.", "warning")
    else:
        solicitud.estado = "NO ENCONTRADO"
        solicitud.razon = safe_string(request.form["razon"])
        solicitud.observaciones_razon = safe_message(request.form["observaciones"])
        solicitud_bitacora = ArcDocumentoBitacora(
            arc_documento=solicitud.arc_documento,
            usuario=current_user,
            observaciones=safe_message(request.form["observaciones"]),
            accion="NO ENCONTRADO",
        )
        solicitud_bitacora.save()
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud NO Encontrada {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/enviar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def send(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "ENCONTRADO":
        flash("No puede enviar si la solicitud no está en estado ENCONTRADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
        flash(f"Solo puede enviar el ROL de {ROL_JEFE_REMESA}.", "warning")
    else:
        solicitud.estado = "ENVIANDO"
        solicitud_bitacora = ArcDocumentoBitacora(
            arc_documento=solicitud.arc_documento,
            usuario=current_user,
            accion="ENVIADO",
        )
        solicitud_bitacora.save()
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud Enviada {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))


@arc_documentos_solicitudes.route("/arc_documentos_solicitudes/recibir/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def receive(solicitud_id):
    """Pasar el estado a RECIBIDO de una Solicitud"""
    solicitud = ArcDocumentoSolicitud.query.get_or_404(solicitud_id)
    documento = ArcDocumento.query.get_or_404(solicitud.arc_documento_id)
    if solicitud.estado != "ENVIANDO":
        flash("No puede RECIBIR si la solicitud no está en estado ENVIANDO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede recibir el ROL de {ROL_SOLICITANTE}.", "warning")
    else:
        solicitud.estado = "ENTREGADO"
        solicitud.usuario_receptor = current_user
        solicitud.tiempo_recepcion = datetime.now()
        solicitud_bitacora = ArcDocumentoBitacora(
            arc_documento=solicitud.arc_documento,
            usuario=current_user,
            accion="ENTREGADO",
        )
        documento.ubicacion = "JUZGADO"
        documento.save()
        solicitud_bitacora.save()
        solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud Recibida {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_documentos_solicitudes.detail", solicitud_id=solicitud_id))
