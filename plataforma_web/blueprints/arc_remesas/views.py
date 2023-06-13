"""
Archivo - Remesas, vistas
"""
import json
from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, not_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.blueprints.arc_remesas_bitacoras.models import ArcRemesaBitacora

from plataforma_web.blueprints.arc_remesas.forms import (
    ArcRemesaNewForm,
    ArcRemesaEditForm,
    ArcRemesaAddDocumentForm,
    ArcRemesaRefuseForm,
    ArcRemesaAsignationForm,
)

from plataforma_web.blueprints.arc_archivos.views import (
    ROL_JEFE_REMESA,
    ROL_ARCHIVISTA,
    ROL_SOLICITANTE,
    ROL_RECEPCIONISTA,
)


MODULO = "ARC REMESAS"


arc_remesas = Blueprint("arc_remesas", __name__, template_folder="templates")


@arc_remesas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_remesas.route("/arc_remesas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Solicitudes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcRemesa.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "remesa_id" in request.form:
        try:
            id = int(request.form["remesa_id"])
            consulta = consulta.filter_by(id=id)
        except:
            pass
        # consulta = consulta.filter_by(id=int(request.form["remesa_id"]))
    if "juzgado_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    if "asignado_id" in request.form:
        try:
            usuario_asignado_id = int(request.form["asignado_id"])
            consulta = consulta.filter_by(usuario_asignado_id=usuario_asignado_id)
        except:
            pass
        # consulta = consulta.filter_by(usuario_asignado_id=int(request.form["asignado_id"]))
    if "anio" in request.form:
        try:
            anio = int(request.form["anio"])
            consulta = consulta.filter_by(anio=anio)
        except:
            pass
        # consulta = consulta.filter_by(anio=int(request.form["anio"]))
    if "tipo_documento" in request.form:
        consulta = consulta.filter_by(tipo_documentos=request.form["tipo_documento"])
    if "num_oficio" in request.form:
        consulta = consulta.filter_by(num_oficio=request.form["num_oficio"])
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    if "esta_archivado" in request.form:
        try:
            esta_archivado = bool(request.form["esta_archivado"])
            consulta = consulta.filter_by(esta_archivado=esta_archivado)
        except:
            pass
        # consulta = consulta.filter_by(esta_archivado=bool(request.form["esta_archivado"]))
    if "omitir_cancelados" in request.form:
        consulta = consulta.filter(ArcRemesa.estado != "CANCELADO")
    if "omitir_pendientes" in request.form:
        consulta = consulta.filter(ArcRemesa.estado != "PENDIENTE")
    if "omitir_archivados" in request.form:
        consulta = consulta.filter(ArcRemesa.esta_archivado != True)
    if "mostrar_archivados" in request.form:
        consulta = consulta.filter_by(esta_archivado=True)
    if "documento_id" in request.form:
        consulta = consulta.join(ArcRemesaDocumento)
        consulta = consulta.filter(ArcRemesaDocumento.arc_documento_id == int(request.form["documento_id"]))
    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    if "orden_acendente" in request.form:
        registros = consulta.order_by(ArcRemesa.id.desc()).offset(start).limit(rows_per_page).all()
    else:
        registros = consulta.order_by(ArcRemesa.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "remesa": {
                    "id": resultado.id,
                    "url": url_for("arc_remesas.detail", remesa_id=resultado.id),
                },
                "juzgado": {
                    "clave": resultado.autoridad.clave,
                    "nombre": resultado.autoridad.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                },
                "tiempo": resultado.modificado.strftime("%Y-%m-%d %H:%M:%S"),
                "anio": resultado.anio,
                "num_oficio": resultado.num_oficio,
                "num_docs": resultado.num_documentos,
                "tipo_documentos": resultado.tipo_documentos,
                "estado": resultado.estado,
                "asignado": {
                    "nombre": "SIN ASIGNAR" if resultado.usuario_asignado is None else resultado.usuario_asignado.nombre,
                    "url": "" if resultado.usuario_asignado is None else url_for("usuarios.detail", usuario_id=resultado.usuario_asignado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_remesas.route("/arc_remesas/<int:remesa_id>")
def detail(remesa_id):
    """Detalle de una Remesa"""
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    current_user_roles = current_user.get_roles()
    mostrar_secciones = {
        "boton_cancelar": False,
        "boton_pasar_historial": False,
    }
    estado_text = {
        "texto": None,
        "class": None,
    }

    # Establece el rol activo
    rol_activo = None
    if ROL_SOLICITANTE in current_user_roles:
        rol_activo = ROL_SOLICITANTE
    elif ROL_JEFE_REMESA in current_user_roles:
        rol_activo = ROL_JEFE_REMESA
    elif ROL_ARCHIVISTA in current_user_roles:
        rol_activo = ROL_ARCHIVISTA
    elif ROL_RECEPCIONISTA in current_user_roles:
        rol_activo = ROL_RECEPCIONISTA

    # Sobre-escribir estados dependiendo del ROL
    estados = {
        ROL_SOLICITANTE: {
            "ASIGNADO": {
                "TEXTO": "PROCESANDO",
                "COLOR": "bg-primary",
            },
        },
        ROL_RECEPCIONISTA: {
            "ASIGNADO": {
                "TEXTO": "PROCESANDO",
                "COLOR": "bg-primary",
            },
        },
        ROL_ARCHIVISTA: {},
        "DEFAULT": {
            "PENDIENTE": "bg-warning text-dark",
            "CANCELADO": "bg-secondary",
            "ENVIADO": "bg-pink",
            "RECHAZADO": "bg-danger",
            "ASIGNADO": "bg-primary",
            "VERIFICADO": "bg-purple",
            "ARCHIVADO": "bg-success",
            "ARCHIVADO CON ANOMALIA": "bg-teal",
        },
    }

    # Sobre-escribe de ser necesario el texto y color del estado dependiendo del ROL activo
    estado_text["texto"] = remesa.estado
    estado_text["class"] = None
    if remesa.estado in estados["DEFAULT"]:
        estado_text["texto"] = remesa.estado
        estado_text["class"] = estados["DEFAULT"][remesa.estado]
    if rol_activo in estados:
        if remesa.estado in estados[rol_activo]:
            if "TEXTO" in estados[rol_activo][remesa.estado]:
                estado_text["texto"] = estados[rol_activo][remesa.estado]["TEXTO"]
            if "COLOR" in estados[rol_activo][remesa.estado]:
                estado_text["class"] = estados[rol_activo][remesa.estado]["COLOR"]

    # Lógica para mostrar secciones
    if remesa.estado == "PENDIENTE":
        if current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
            mostrar_secciones["boton_cancelar"] = True
            return render_template(
                "arc_remesas/detail_solicitante.jinja2",
                remesa=remesa,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_documentos=json.dumps({"remesa_id": remesa.id}),
                filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
            )
        else:
            flash("Su rol no tiene permitido ver remesas en estado PENDIENTE", "warning")
            return redirect(url_for("arc_archivos.list_active"))

    if remesa.estado == "CANCELADO":
        if ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
            if not remesa.esta_archivado:
                mostrar_secciones["boton_pasar_historial"] = True
                mostrar_secciones["boton_recuperar"] = True
                return render_template(
                    "arc_remesas/detail_solicitante.jinja2",
                    remesa=remesa,
                    mostrar_secciones=mostrar_secciones,
                    estado_text=estado_text,
                    filtros_documentos=json.dumps({"remesa_id": remesa.id}),
                    filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
                )

    if remesa.estado == "ENVIADO":
        if ROL_JEFE_REMESA in current_user_roles:
            mostrar_secciones["asignar"] = True
            mostrar_secciones["rechazar"] = True
            form = ArcRemesaAsignationForm()
            archivistas = Usuario.query.join(UsuarioRol).join(Rol)
            archivistas = archivistas.filter(Rol.nombre == ROL_ARCHIVISTA)
            archivistas = archivistas.filter(UsuarioRol.estatus == "A").filter(Usuario.estatus == "A").filter(Rol.estatus == "A")
            archivistas = archivistas.all()
            return render_template(
                "arc_remesas/detail.jinja2",
                remesa=remesa,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_documentos=json.dumps({"remesa_id": remesa.id}),
                filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
                archivistas=archivistas,
            )

    if remesa.estado == "ASIGNADO":
        mostrar_secciones["asignado"] = True
        if ROL_JEFE_REMESA in current_user_roles:
            mostrar_secciones["asignar"] = True
            archivistas = Usuario.query.join(UsuarioRol).join(Rol)
            archivistas = archivistas.filter(Rol.nombre == ROL_ARCHIVISTA)
            archivistas = archivistas.filter(UsuarioRol.estatus == "A").filter(Usuario.estatus == "A").filter(Rol.estatus == "A")
            archivistas = archivistas.all()
            form = ArcRemesaAsignationForm()
            form.asignado.data = remesa.usuario_asignado
            return render_template(
                "arc_remesas/detail.jinja2",
                remesa=remesa,
                form=form,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_documentos=json.dumps({"remesa_id": remesa.id}),
                filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
                archivistas=archivistas,
            )
        if ROL_ARCHIVISTA in current_user_roles:
            # Revisar si no hay documentos anexos dentro de la remesa
            documentos_anexos_count = ArcRemesaDocumento.query.join(ArcDocumento)
            documentos_anexos_count = documentos_anexos_count.filter(ArcRemesaDocumento.arc_remesa_id == remesa_id)
            documentos_anexos_count = documentos_anexos_count.filter(ArcDocumento.ubicacion == "REMESA")
            documentos_anexos_count = documentos_anexos_count.count()
            if documentos_anexos_count == 0:
                mostrar_secciones["boton_completado"] = True
            return render_template(
                "arc_remesas/detail_archivista.jinja2",
                remesa=remesa,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros_documentos=json.dumps({"remesa_id": remesa.id}),
                filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
            )

    if remesa.estado == "RECHAZADO":
        mostrar_secciones["rechazo"] = True
        if ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
            if not remesa.esta_archivado:
                mostrar_secciones["boton_pasar_historial"] = True

    if remesa.estado == "ARCHIVADO" or remesa.estado == "ARCHIVADO CON ANOMALIA":
        if ROL_SOLICITANTE in current_user_roles or ROL_RECEPCIONISTA in current_user_roles:
            if not remesa.esta_archivado:
                mostrar_secciones["boton_pasar_historial"] = True

    # Por defecto mostramos solo los detalles de la remesa
    return render_template(
        "arc_remesas/detail.jinja2",
        remesa=remesa,
        mostrar_secciones=mostrar_secciones,
        estado_text=estado_text,
        filtros_documentos=json.dumps({"remesa_id": remesa.id}),
        filtros_bitacora=json.dumps({"remesa_id": remesa.id}),
    )


@arc_remesas.route("/arc_remesas/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Remesa"""

    form = ArcRemesaNewForm()
    if form.validate_on_submit():
        if form.anio.data < 1900 or form.anio.data > date.today().year:
            flash(f"El año se encuentra fuera de un rango permitido 1900-{date.today().year}.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
            flash(f"Solo se pueden crear nuevas remesas por el Administrador o {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        else:
            remesa = ArcRemesa(
                autoridad=current_user.autoridad,
                esta_archivado=False,
                anio=int(form.anio.data),
                tipo_documentos=form.tipo_documentos.data,
                num_oficio=safe_string(form.num_oficio.data),
                estado="PENDIENTE",
                num_documentos=0,
                num_anomalias=0,
            ).save()
            # Guardado de acción en bitacora de la remesa
            ArcRemesaBitacora(
                arc_remesa=remesa,
                usuario=current_user,
                accion="CREADA",
            ).save()
            # Guardado de registro en bitacora del sistema
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Remesa creada {remesa.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("arc_remesas/new.jinja2", form=form)


@arc_remesas.route("/arc_remesas/cancelar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(remesa_id):
    """Cancelar Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede cancelar remesas el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Validar Remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    if remesa.estatus != "A":
        flash("La Remesa seleccionada está eliminada.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.estado != "PENDIENTE":
        flash("La Remesa NO se encuentra en estado PENDIENTE. No se puede CANCELAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.esta_archivado:
        flash("La Remesa se encuentra archivada. No se puede CANCELAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Cancelar Remesa
    remesa.estado = "CANCELADO"
    remesa.save()
    # Guardado de acción en bitacora de la remesa
    ArcRemesaBitacora(
        arc_remesa=remesa,
        usuario=current_user,
        accion="CANCELADA",
    ).save()

    flash("La Remesa ha sido CANCELADA correctamente.", "success")
    return redirect(url_for("arc_archivos.list_active"))


@arc_remesas.route("/arc_remesas/recuperar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(remesa_id):
    """Recuperar Remesa Cancelada"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede RECUPERAR una remesas el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Validar Remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    if remesa.estatus != "A":
        flash("La Remesa seleccionada está eliminada.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.estado != "CANCELADO":
        flash("La Remesa NO se encuentra en estado CANCELADO. No se puede RECUPERAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.esta_archivado:
        flash("La Remesa se encuentra archivada. No se puede RECUPERAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # revisar que sus documentos anexos no se encuentren en otras remesas en proceso
    documento_ocupado = False
    documentos = ArcRemesaDocumento.query.filter_by(arc_remesa_id=remesa_id).all()
    for documento in documentos:
        documento_anexo = ArcRemesaDocumento.query.join(ArcRemesa).filter(ArcRemesaDocumento.arc_remesa_id != remesa_id)
        documento_anexo = documento_anexo.filter(or_(ArcRemesa.estado != "CANCELADO", ArcRemesa.estado != "ARCHIVADO"))
        documento_anexo = documento_anexo.filter(ArcRemesaDocumento.arc_documento_id == documento.arc_documento.id).filter_by(estatus="A").first()
        if documento_anexo:
            documento_ocupado = documento_anexo
            break
    if documento_ocupado:
        flash(f"La Remesa contiene un documento [{documento_anexo.arc_documento.expediente}] adjunto que está siendo utilizado en otra remesa activa [{documento_anexo.arc_remesa_id}]. No se puede RECUPERAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Cancelar Remesa
    remesa.estado = "PENDIENTE"
    remesa.save()

    flash("La Remesa ha sido RECUPERADA correctamente.", "success")
    return redirect(url_for("arc_archivos.list_active"))


@arc_remesas.route("/arc_remesas/editar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(remesa_id):
    """Editar Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede EDITAR una remesas el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Validar Remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    if remesa.estatus != "A":
        flash("La Remesa seleccionada está eliminada.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.estado != "PENDIENTE":
        flash("Solo se puede EDITAR una Remesa si se encuentra en estado PENDIENTE.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
    elif remesa.esta_archivado:
        flash("La Remesa se encuentra ARCHIVADA. No se puede EDITAR.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    form = ArcRemesaEditForm()
    if form.validate_on_submit():
        remesa.anio = form.anio.data
        remesa.num_oficio = safe_string(form.num_oficio.data)
        remesa.observaciones = safe_message(form.observaciones.data, default_output_str=None)
        remesa.save()

        # Agregamos a la bitácora la acción realizada
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Remesa editada {remesa.id}"),
            url=url_for("arc_remesas.detail", remesa_id=remesa_id),
        )
        bitacora.save()
        flash("La Remesa se ACTUALIZÓ correctamente.", "success")
        return redirect(bitacora.url)

    # Datos pre-cargados
    form.creado_readonly.data = remesa.creado.strftime("%Y/%m/%d - %H:%M %p")
    form.juzgado_readonly.data = remesa.autoridad.clave + " : " + remesa.autoridad.descripcion_corta
    form.tipo_documentos_readonly.data = remesa.tipo_documentos
    form.anio.data = remesa.anio
    form.num_oficio.data = remesa.num_oficio
    form.observaciones.data = remesa.observaciones

    # Entregar template
    return render_template("arc_remesas/edit.jinja2", remesa_id=remesa_id, form=form)


@arc_remesas.route("/arc_remesas/enviar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def send(remesa_id):
    """Enviar Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede enviar remesas el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        return redirect(url_for("arc_archivos.list_active"))

    # Validar Remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    if remesa.estatus != "A":
        flash("La Remesa seleccionada está eliminado.", "warning")
        return redirect(url_for("arc_archivos.list_active"))
    elif remesa.estado != "PENDIENTE":
        flash("La Remesa NO se encuentra en estado de PENDIENTE. No se puede enviar.", "warning")
        return redirect(url_for("arc_archivos.list_active"))

    # Validar que tenga documentos adjuntos
    num_documentos = ArcRemesaDocumento.query.filter_by(arc_remesa_id=remesa.id).count()
    if num_documentos is None or num_documentos < 1:
        flash("No se puede enviar una remesa sin documentos adjuntos.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Cambiar de ubicación los documentos anexos
    documentos = ArcRemesaDocumento.query.filter_by(arc_remesa_id=remesa_id).all()
    for documento in documentos:
        documento.arc_documento.ubicacion = "REMESA"
        documento.save()

    # Enviar Remesa
    remesa.estado = "ENVIADO"
    remesa.tiempo_enviado = datetime.now()
    remesa.save()
    # Guardado de acción en bitacora de la remesa
    remesa_bitacora = ArcRemesaBitacora(
        arc_remesa=remesa,
        usuario=current_user,
        accion="ENVIADA",
    ).save()
    # Guardado de registro en bitacora del sistema
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Remesa enviada {remesa.id}"),
        url=url_for("arc_archivos.list_active"),
    ).save()

    # Resultado final exitoso
    flash("La Remesa ha sido enviada correctamente.", "success")
    return redirect(url_for("arc_archivos.list_active"))


@arc_remesas.route("/arc_remesas/agregar_documento/<int:documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def add_document(documento_id):
    """Añadir documento a Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede editar remesas el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
        return redirect(url_for("arc_documentos.list_active"))

    # Validar Documento
    documento = ArcDocumento.query.get_or_404(documento_id)
    if documento.estatus != "A":
        flash("El documento seleccionado está eliminado.", "warning")
        return redirect("arc_documentos.list_active")
    elif documento.ubicacion != "JUZGADO":
        flash("El documento se encuentra en una ubicación diferente a JUZGADO.", "warning")
        return redirect("arc_documentos.list_active")
    # Buscar si el documento ya está en otra remesa pendiente
    documento_en_otra_remesa = ArcRemesaDocumento.query.join(ArcRemesa)
    documento_en_otra_remesa = documento_en_otra_remesa.filter(ArcRemesaDocumento.arc_documento_id == documento_id)
    documento_en_otra_remesa = documento_en_otra_remesa.filter(ArcRemesa.estado != "CANCELADO").filter(ArcRemesa.estado != "ARCHIVADO").filter(ArcRemesa.estado != "RECHAZADO").first()
    if documento_en_otra_remesa:
        if documento_en_otra_remesa.arc_remesa.estado not in ("CANCELADO", "ARCHIVADO", "RECHAZADO", "ARCHIVADO CON ANOMALIA"):
            flash(f"Este documento ya está asignado a la remesa [{documento_en_otra_remesa.arc_remesa.id}] que se encuentra en proceso.", "warning")
            return redirect(url_for("arc_documentos.detail", documento_id=documento_id))
        if documento_en_otra_remesa.arc_remesa.estatus != "A":
            flash("Esta Remesa está eliminada.", "warning")
            return redirect(url_for("arc_documentos.list_active"))

    # Validar el Formulario
    form = ArcRemesaAddDocumentForm()
    if form.validate_on_submit():
        # Validar la Remesa
        remesa = ArcRemesa.query.get_or_404(form.remesas.data)
        if remesa.autoridad_id != current_user.autoridad.id:
            flash("La remesa NO pertenece a su Autoridad.", "warning")
        elif remesa.estado != "PENDIENTE":
            flash("La remesa NO tiene un estado de PENDIENTE.", "warning")
        elif remesa.esta_archivado:
            flash("La remesa se encuentra ARCHIVADA, ya no puede ser modificada.", "warning")
        elif remesa.tipo_documentos != documento.tipo:
            flash(f"La remesa solo puede contener documentos del tipo {remesa.tipo_documentos}.", "warning")
        elif remesa.estatus != "A":
            flash("La remesa está eliminada.", "warning")
        else:
            documento_agregar = ArcRemesaDocumento(
                arc_documento=documento,
                arc_remesa=remesa,
                fojas=form.fojas.data,
                tipo_juzgado=form.tipo_juzgado.data,
                observaciones_solicitante=safe_message(form.observaciones.data, default_output_str=None),
            )
            documento_agregar.save()
            # Actualizar el número de documentos anexos de la remesa
            remesa.num_documentos = ArcRemesaDocumento.query.filter_by(arc_remesa=remesa).count()
            remesa.save()
            # Mostrar mensaje de éxito.
            flash(f"Se añadió el documento {documento.id} a la remesa {remesa.id}, correctamente.", "success")
            return redirect(url_for("arc_remesas.detail", remesa_id=remesa.id))

    # Datos sugeridos para el formulario
    form.fojas.data = documento.fojas
    form.tipo_juzgado.data = documento.tipo_juzgado
    remesas = ArcRemesa.query.filter_by(autoridad_id=current_user.autoridad.id).filter_by(estado="PENDIENTE").filter_by(estatus="A").all()

    return render_template("arc_remesas/add_document.jinja2", remesas=remesas, documento=documento, form=form)


@arc_remesas.route("/arc_remesas/asignar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def asign(remesa_id):
    """Asignar Remesa a un Archivista"""
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    form = ArcRemesaAsignationForm()
    if form.validate_on_submit():
        if remesa.estado != "ENVIADO" and remesa.estado != "ASIGNADO":
            flash("No puede asignar a alguien estando la Remesa en un estado diferente a ENVIADO o ASIGNADO.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
            flash(f"Solo puede asignar el ROL de {ROL_JEFE_REMESA}.", "warning")
        else:
            if form.asignado.data is None or form.asignado.data == "":
                remesa.estado = "ENVIADO"
                remesa.usuario_asignado = None
            else:
                remesa.estado = "ASIGNADO"
                remesa.usuario_asignado_id = int(form.asignado.data)
            remesa.save()
            # Guardado de acción en bitacora de la remesa
            if remesa.usuario_asignado is None:
                observacion = "Des-asignado"
            else:
                observacion = f"Asigando a: {remesa.usuario_asignado.nombre}."
            remesa_bitacora = ArcRemesaBitacora(
                arc_remesa=remesa,
                usuario=current_user,
                accion="ASIGNADA",
                observaciones=observacion,
            ).save()
            # Guardado de registro en bitacora del sistema
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Asignación de Archivista a Remesa {remesa.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))


@arc_remesas.route("/arc_remesas/rechazar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def refuse(remesa_id):
    """Rechazar Remesa"""
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    form = ArcRemesaRefuseForm()
    if form.validate_on_submit():
        if remesa.estado != "ENVIADO":
            flash("No puede rechazar la Remesa en un estado diferente a ENVIADO.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_JEFE_REMESA not in current_user.get_roles():
            flash(f"Solo puede rechazar el ROL de {ROL_JEFE_REMESA}.", "warning")
        else:
            # Cambiar de ubicación los documentos anexos
            documentos = ArcRemesaDocumento.query.filter_by(arc_remesa_id=remesa_id).all()
            for documento in documentos:
                documento.arc_documento.ubicacion = "JUZGADO"
                documento.save()

            remesa.rechazo = safe_message(form.observaciones.data)
            remesa.estado = "RECHAZADO"
            remesa.save()
            # Guardado de acción en bitacora de la remesa
            remesa_bitacora = ArcRemesaBitacora(
                arc_remesa=remesa,
                usuario=current_user,
                accion="RECHAZADA",
                observaciones=remesa.rechazo,
            ).save()
            # Guardado de registro en bitacora del sistema
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Se ha rechazado la Remesa {remesa.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)

    # Template con formulario de rechazo
    return render_template("arc_remesas/refuse.jinja2", remesa=remesa, form=form)


@arc_remesas.route("/arc_remesas/pasar_historial/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def history(remesa_id):
    """Pasar al historial una Remesa"""
    remesa = ArcRemesa.query.get_or_404(remesa_id)
    if remesa.estado not in ["CANCELADO", "RECHAZADO", "ARCHIVADO", "ARCHIVADO CON ANOMALIA"]:
        flash("No puede pasar al historial una remesa en este estado.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles() and ROL_RECEPCIONISTA not in current_user.get_roles():
        flash(f"Solo puede pasar al historial el ROL de {ROL_SOLICITANTE} o {ROL_RECEPCIONISTA}.", "warning")
    else:
        remesa.esta_archivado = True
        remesa.save()
        # Guardado de acción en bitacora de la remesa
        ArcRemesaBitacora(
            arc_remesa=remesa,
            usuario=current_user,
            accion="PASADA AL HISTORIAL",
        ).save()
        # Guardado de registro en bitacora del sistema
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Remesa {remesa.id} pasada al Historial."),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))


@arc_remesas.route("/arc_remesas/completar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def complete(remesa_id):
    """Pasar a ARCHIVADO una Remesa"""

    # Localizamos el documento anexo de la remesa
    remesa = ArcRemesa.query.get_or_404(remesa_id)

    # Validamos remesa
    if remesa.estado != "ASIGNADO":
        flash("Solo las remesas en estado ASIGNADO pueden pasar a COMPLETADO.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Validamos los roles que pueden realizar dicha acción
    current_user_roles = current_user.get_roles()
    if not (ROL_ARCHIVISTA in current_user_roles or current_user.can_admin(MODULO)):
        flash("Solo el rol de ARCHIVISTA puede ARCHIVAR una Remesa.", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Validamos si todos sus anexos fuera de la REMESA
    documentos_anexos_count = ArcRemesaDocumento.query.join(ArcDocumento)
    documentos_anexos_count = documentos_anexos_count.filter(ArcRemesaDocumento.arc_remesa_id == remesa_id)
    documentos_anexos_count = documentos_anexos_count.filter(ArcDocumento.ubicacion == "REMESA")
    documentos_anexos_count = documentos_anexos_count.count()
    if documentos_anexos_count > 0:
        flash(f"Hay {documentos_anexos_count} documentos anexos sin archivar. Necesita que todos estén archivados para archivar la remesa", "warning")
        return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))

    # Guardar cambios a la Remesa
    if remesa.num_anomalias > 0:
        remesa.estado = "ARCHIVADO CON ANOMALIA"
        remesa.save()
        # Guardado de acción en bitacora de la remesa
        ArcRemesaBitacora(
            arc_remesa=remesa,
            usuario=current_user,
            accion="ARCHIVADA CON ANOMALIA",
            observaciones=safe_message(f"Núm. de Anomalías: {remesa.num_anomalias}"),
        ).save()
    else:
        remesa.estado = "ARCHIVADO"
        remesa.save()
        # Guardado de acción en bitacora de la remesa
        ArcRemesaBitacora(
            arc_remesa=remesa,
            usuario=current_user,
            accion="ARCHIVADA",
            observaciones=safe_message(f"Núm. de Docs: {remesa.num_documentos}"),
        ).save()
    # Guardado de registro en bitacora del sistema
    Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Nueva Remesa creada {remesa.id}"),
        url=url_for("arc_archivos.list_active"),
    ).save()

    # Resultado final de éxito
    flash(f"La Remesa {remesa.id} ha sido ARCHIVADA correctamente.", "success")
    return redirect(url_for("arc_archivos.list_active"))


@arc_remesas.route("/arc_remesas/imprimir_listado/", methods=["GET", "POST"])
def print_list():
    """Pagina de impresión de listado de Remesas"""

    # Preparar la consulta
    remesas = ArcRemesa.query.filter_by(esta_archivado=False).filter_by(estatus="A")

    # Asignación por Roles
    current_user_roles = current_user.get_roles()
    if ROL_ARCHIVISTA in current_user_roles:
        remesas = remesas.filter_by(usuario_asignado=current_user)

    # Listar todas las remesas
    remesas = remesas.all()

    # Resultado para impresión
    return render_template("arc_remesas/print_list.jinja2", remesas=remesas)
