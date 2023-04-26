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

from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_solicitudes_bitacoras.models import ArcSolicitudBitacora
from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.blueprints.arc_solicitudes.forms import ArcSolicitudNewForm, ArcSolicitudAsignationForm, ArcSolicitudFoundForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE, ROL_RECEPCIONISTA


MODULO = "ARC SOLICITUDES"


arc_solicitudes = Blueprint("arc_solicitudes", __name__, template_folder="templates")


@arc_solicitudes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_solicitudes.route("/arc_solicitudes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Solicitudes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcSolicitud.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "solicitud_id" in request.form:
        try:
            id = int(request.form["solicitud_id"])
            consulta = consulta.filter_by(id=id)
        except ValueError:
            pass
        # consulta = consulta.filter_by(id=int(request.form["solicitud_id"]))
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    if "juzgado_id" in request.form:
        try:
            autoridad_id = int(request.form["juzgado_id"])
            consulta = consulta.filter_by(autoridad_id=autoridad_id)
        except ValueError:
            pass
        # consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    if "asignado_id" in request.form:
        try:
            usuario_asignado_id = int(request.form["asignado_id"])
            consulta = consulta.filter_by(usuario_asignado_id=usuario_asignado_id)
        except ValueError:
            pass
        # consulta = consulta.filter_by(usuario_asignado_id=int(request.form["asignado_id"]))
    if "arc_documento_id" in request.form:
        try:
            arc_documento_id = int(request.form["arc_documento_id"])
            consulta = consulta.filter_by(arc_documento_id=arc_documento_id)
        except ValueError:
            pass
        # consulta = consulta.filter_by(arc_documento_id=int(request.form["arc_documento_id"]))
    if "esta_archivado" in request.form:
        try:
            esta_archivado = bool(request.form["esta_archivado"])
            consulta = consulta.filter_by(esta_archivado=esta_archivado)
        except ValueError:
            pass
        # consulta = consulta.filter_by(esta_archivado=bool(request.form["esta_archivado"]))
    if "omitir_cancelados" in request.form:
        consulta = consulta.filter(ArcSolicitud.estado != "CANCELADO")
    if "omitir_archivados" in request.form:
        consulta = consulta.filter(ArcSolicitud.esta_archivado != True)
    if "mostrar_archivados" in request.form:
        consulta = consulta.filter_by(esta_archivado=True)
    if "expediente" in request.form:
        consulta = consulta.join(ArcDocumento)
        consulta = consulta.filter(ArcDocumento.expediente.contains(request.form["expediente"]))
    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    if "orden_acendente" in request.form:
        registros = consulta.order_by(ArcSolicitud.id.desc()).offset(start).limit(rows_per_page).all()
    else:
        registros = consulta.order_by(ArcSolicitud.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "solicitud": {
                    "id": resultado.id,
                    "url": url_for("arc_solicitudes.detail", solicitud_id=resultado.id),
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


@arc_solicitudes.route("/arc_solicitudes/<int:solicitud_id>")
def detail(solicitud_id):
    """Detalle de una Solicitud"""

    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
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
    if solicitud.estado == "SOLICITADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles):
        mostrar_secciones["boton_cancelar_solicitud"] = True
    if solicitud.estado == "CANCELADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
    if solicitud.estado == "ASIGNADO" and (current_user.can_admin(MODULO) or ROL_ARCHIVISTA in current_user_roles):
        mostrar_secciones["formulario_encontrado"] = True
        mostrar_secciones["archivista"] = True
    if solicitud.estado == "NO ENCONTRADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
        mostrar_secciones["archivista"] = True
    if solicitud.estado == "ENTREGADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True
        mostrar_secciones["archivista"] = True
    if solicitud.esta_archivado:
        mostrar_secciones["boton_pasar_historial"] = False

    # Mostrar vista con formulario de asignación
    if solicitud.estado == "SOLICITADO" or solicitud.estado == "ASIGNADO":
        if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles:
            mostrar_secciones["archivista"] = True
            form = ArcSolicitudAsignationForm()
            archivistas = Usuario.query.join(UsuarioRol).join(Rol)
            archivistas = archivistas.filter(Rol.nombre == ROL_ARCHIVISTA)
            archivistas = archivistas.filter(UsuarioRol.estatus == "A").filter(Usuario.estatus == "A").filter(Rol.estatus == "A")
            archivistas = archivistas.all()
            return render_template(
                "arc_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                archivistas=archivistas,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
            )
    if solicitud.estado == "ASIGNADO":
        if current_user.can_admin(MODULO) or ROL_ARCHIVISTA in current_user_roles:
            form = ArcSolicitudFoundForm()
            form.fojas.data = solicitud.arc_documento.fojas
            return render_template(
                "arc_solicitudes/detail.jinja2",
                solicitud=solicitud,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
            )
    if solicitud.estado == "NO ENCONTRADO":
        mostrar_secciones["archivista"] = True
        return render_template(
            "arc_solicitudes/detail.jinja2",
            solicitud=solicitud,
            mostrar_secciones=mostrar_secciones,
            estado_text=estado_text,
            filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
        )
    if solicitud.estado == "ENCONTRADO":
        mostrar_secciones["archivista"] = True
        if current_user.can_admin(MODULO) or ROL_JEFE_REMESA in current_user_roles:
            mostrar_secciones["enviar"] = True
            return render_template(
                "arc_solicitudes/detail.jinja2",
                solicitud=solicitud,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
            )
    if solicitud.estado == "ENVIANDO":
        mostrar_secciones["archivista"] = True
        if current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
            mostrar_secciones["recibir"] = True
            return render_template(
                "arc_solicitudes/detail.jinja2",
                solicitud=solicitud,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
            )
    if solicitud.estado == "ENTREGADO":
        mostrar_secciones["entregado"] = True
        usuario_receptor = Usuario.query.get_or_404(solicitud.usuario_receptor_id)
        return render_template(
            "arc_solicitudes/detail.jinja2",
            solicitud=solicitud,
            mostrar_secciones=mostrar_secciones,
            estado_text=estado_text,
            usuario_receptor=usuario_receptor,
            filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
        )

    # Por defecto mostramos solo los detalles de la solicitud
    return render_template(
        "arc_solicitudes/detail.jinja2",
        solicitud=solicitud,
        mostrar_secciones=mostrar_secciones,
        estado_text=estado_text,
        filtros_bitacora=json.dumps({"solicitud_id": solicitud.id, "estatus": "A"}),
    )


@arc_solicitudes.route("/arc_solicitudes/nuevo/<int:documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(documento_id):
    """Nuevo Documento"""
    documento = ArcDocumento.query.get_or_404(documento_id)
    form = ArcSolicitudNewForm()
    if form.validate_on_submit():
        current_user_roles = current_user.get_roles()
        if documento.ubicacion != "ARCHIVO":
            flash("El documento solo puede ser solicitado cuando su ubicación está en ARCHIVO.", "warning")
            return render_template("arc_solicitudes/new.jinja2", documento_id=documento.id, form=form)
        elif documento.autoridad_id != current_user.autoridad.id:
            if not (current_user.can_admin(MODULO) or ROL_RECEPCIONISTA in current_user_roles):
                flash(f"Solo se pueden solicitar documentos de la misma Autoridad.", "warning")
                return render_template("arc_solicitudes/new.jinja2", documento_id=documento.id, form=form)
        elif ArcSolicitud.query.filter_by(arc_documento=documento).filter_by(esta_archivado=False).filter_by(estatus="A").first():
            flash("Este documento ya se encuentra en proceso de solicitud.", "warning")
            return render_template("arc_solicitudes/new.jinja2", documento_id=documento.id, form=form)
        # Crear Solicitud
        num_folio = safe_string(form.num_folio.data)
        if num_folio == "":
            num_folio = None
        solicitud = ArcSolicitud(
            arc_documento=documento,
            autoridad=current_user.autoridad,
            usuario_receptor_id=None,
            tiempo_recepcion=None,
            esta_archivado=False,
            num_folio=num_folio,
            observaciones_solicitud=safe_message(form.observaciones.data, default_output_str=None),
            estado="SOLICITADO",
        )
        solicitud.save()
        # Añadir acción a la bitácora de Solicitudes
        observaciones = ""
        if num_folio is not None:
            observaciones += f"Núm. Folio: {num_folio}."
        if solicitud.observaciones_solicitud is not None:
            observaciones += solicitud.observaciones_solicitud
        observaciones = safe_message(observaciones, default_output_str=None)
        if observaciones == "":
            observaciones = None
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="SOLICITADA",
            observaciones=observaciones,
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Solicitud de Documento {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Carga de datos en el formulario
    form.num_expediente.data = documento.expediente
    form.anio.data = documento.anio
    form.actor.data = documento.actor
    form.demandado.data = documento.demandado
    form.juicio.data = documento.juicio
    form.tipo_juzgado.data = documento.tipo_juzgado
    form.juzgado_origen.data = documento.arc_juzgado_origen.nombre if documento.arc_juzgado_origen is not None else ""
    form.tipo.data = documento.tipo
    form.fojas_actuales.data = documento.fojas
    form.ubicacion.data = documento.ubicacion
    return render_template("arc_solicitudes/new.jinja2", documento_id=documento.id, form=form)


@arc_solicitudes.route("/arc_solicitudes/asignar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def assign(solicitud_id):
    """Asignar solicitud a Archivista"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    form = ArcSolicitudAsignationForm()
    if form.validate_on_submit():
        if solicitud.estado != "SOLICITADO" and solicitud.estado != "ASIGNADO":
            flash("No puede asignar a alguien estando la solicitud en un estado diferente a SOLICITADO o ASIGNADO.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
            flash(f"Solo puede asignar el ROL de {ROL_JEFE_REMESA}.", "warning")
        else:
            observaciones = ""
            if form.asignado.data is None or form.asignado.data == "":
                solicitud.estado = "SOLICITADO"
                solicitud.usuario_asignado = None
                observaciones = (safe_message("Desasignado", default_output_str=None),)
            else:
                solicitud.estado = "ASIGNADO"
                solicitud.usuario_asignado_id = int(form.asignado.data)
                observaciones = (safe_message(f"Asigando a: {solicitud.usuario_asignado.nombre}", default_output_str=None),)
            solicitud.save()
            # Añadir acción a la bitácora de Solicitudes
            ArcSolicitudBitacora(
                arc_solicitud=solicitud,
                usuario=current_user,
                accion="ASIGNADA",
                observaciones=observaciones,
            ).save()
            # Añadir acción a la bitácora del Sistem
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Asignación de Archivista a Solicitud {solicitud.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/cancelar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(solicitud_id):
    """Cancelar una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "SOLICITADO":
        flash("No puede cancelar una solicitud en un estado diferente a SOLICITADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede cancelar el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}..", "warning")
    else:
        solicitud.estado = "CANCELADO"
        solicitud.save()
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="CANCELADA",
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Se ha cancelado con éxito la Solicitud: {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/pasar_historial/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def history(solicitud_id):
    """Pasar al historial una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado not in ["CANCELADO", "NO ENCONTRADO", "ENTREGADO"]:
        flash("No puede pasar al historial una solicitud en este estado.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede pasar al historial el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
    else:
        solicitud.esta_archivado = True
        solicitud.save()
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="PASADA AL HISTORIAL",
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud {solicitud.id} pasada al Historial."),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/encontrado/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def found(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    documento = ArcDocumento.query.get_or_404(solicitud.arc_documento_id)
    if solicitud.estado != "ASIGNADO":
        flash("No puede cambiar el estado a ENCONTRADO de una solicitud que está en un estado diferente a ASIGNADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_ARCHIVISTA not in current_user.get_roles():
        flash(f"Solo puede cambiar el estado a ENCONTRADO el ROL de {ROL_ARCHIVISTA}.", "warning")
    else:
        fojas = 0
        observaciones = ""
        if "fojas" in request.form:
            fojas = int(request.form["fojas"])
        if fojas is None or fojas == "":
            fojas = 0
        solicitud.estado = "ENCONTRADO"
        if fojas > 0 and documento.fojas != fojas:
            documento.fojas = fojas
            documento.save()
            if "fojas" in request.form or "observaciones" in request.form:
                solicitud_bitacora = ArcDocumentoBitacora(
                    arc_documento=solicitud.arc_documento,
                    usuario=current_user,
                    fojas=fojas,
                    observaciones=safe_message(request.form["observaciones"], default_output_str=None),
                    accion="CORRECCION FOJAS",
                )
                observaciones = f"Tuvo corrección en Fojas de {documento.fojas} a {fojas}."
                solicitud_bitacora.save()
        else:
            observaciones = safe_message(request.form["observaciones"], default_output_str=None)
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="ENCONTRADA",
            observaciones=safe_message(observaciones, default_output_str=None),
        ).save()
        # Añadir acción a la bitácora del Sistema
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
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/no_encontrado/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def no_found(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
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
        # Añadir acción a la bitácora de Solicitudes
        observaciones = safe_message(request.form["observaciones"], default_output_str=None)
        observaciones = f"Razón: {solicitud.razon}. {observaciones}"
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="NO ENCONTRADA",
            observaciones=observaciones,
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud NO Encontrada {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/enviar/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def send(solicitud_id):
    """Pasar el estado a ENCONTRADO de una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "ENCONTRADO":
        flash("No puede enviar si la solicitud no está en estado ENCONTRADO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
        flash(f"Solo puede enviar el ROL de {ROL_JEFE_REMESA}.", "warning")
    else:
        solicitud.estado = "ENVIANDO"
        solicitud.save()
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="ENVIADA",
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud Enviada {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/recibir/<int:solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def receive(solicitud_id):
    """Pasar el estado a RECIBIDO de una Solicitud"""
    solicitud = ArcSolicitud.query.get_or_404(solicitud_id)
    documento = ArcDocumento.query.get_or_404(solicitud.arc_documento_id)
    if solicitud.estado != "ENVIANDO":
        flash("No puede RECIBIR si la solicitud no está en estado ENVIANDO.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede recibir el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
    else:
        solicitud.estado = "ENTREGADO"
        solicitud.usuario_receptor_id = current_user.id
        solicitud.tiempo_recepcion = datetime.now()
        documento.ubicacion = "JUZGADO"
        documento.save()
        solicitud.save()
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,
            accion="ENTREGADA",
        ).save()
        # Añadir acción a la bitácora del Sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Solicitud Recibida {solicitud.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_solicitudes.detail", solicitud_id=solicitud_id))


@arc_solicitudes.route("/arc_solicitudes/imprimir_listado/", methods=["GET", "POST"])
def print_list():
    """Pagina de impresión de listado de Solicitudes Activas por ROL"""

    # Preparar la consulta
    solicitudes = ArcSolicitud.query.filter_by(esta_archivado=False).filter_by(estatus="A")

    # Asignación por Roles
    current_user_roles = current_user.get_roles()
    if ROL_ARCHIVISTA in current_user_roles:
        solicitudes = solicitudes.filter_by(usuario_asignado=current_user)

    # Listar todas las solicitudes
    solicitudes = solicitudes.all()

    # Resultado para impresión
    return render_template("arc_solicitudes/print_list.jinja2", solicitudes=solicitudes)
