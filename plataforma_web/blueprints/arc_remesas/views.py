"""
Archivo - Remesas, vistas
"""
import json
from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.blueprints.arc_remesas.forms import ArcRemesaNewForm, ArcRemesaAddDocumentForm, ArcRemesaAsignationForm, ArcRemesaRefuseForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE


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
    if "juzgado_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    if "asignado_id" in request.form:
        consulta = consulta.filter_by(usuario_asignado_id=int(request.form["asignado_id"]))
    if "esta_archivado" in request.form:
        consulta = consulta.filter_by(esta_archivado=bool(request.form["esta_archivado"]))
    if "omitir_cancelados" in request.form:
        consulta = consulta.filter(ArcRemesa.estado != "CANCELADO")
    if "omitir_pendientes" in request.form:
        consulta = consulta.filter(ArcRemesa.estado != "PENDIENTE")
    if "omitir_archivados" in request.form:
        consulta = consulta.filter(ArcRemesa.esta_archivado != True)
    if "mostrar_archivados" in request.form:
        consulta = consulta.filter_by(esta_archivado=True)
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
                "num_docs": ArcRemesaDocumento.query.filter_by(arc_remesa_id=resultado.id).filter_by(estatus="A").count(),
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

    # Sobre-escribir estados dependiendo del ROL
    estados = {
        ROL_SOLICITANTE: {},
        ROL_ARCHIVISTA: {},
        "DEFAULT": {
            "PENDIENTE": "bg-warning text-dark",
            "CANCELADO": "bg-secondary",
            "ENVIADO": "bg-pink",
            "RECHAZADO": "bg-danger",
            "ASIGNADO": "bg-primary",
            "VERIFICADO": "bg-purple",
            "ARCHIVADO": "bg-success",
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
        if current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles:
            return render_template(
                "arc_remesas/detail_edit.jinja2",
                remesa=remesa,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros=json.dumps({"remesa_id": remesa.id}),
            )
        else:
            flash("Su rol no tiene permitido ver remesas en estado PENDIENTE", "warning")
            return redirect(url_for("arc_archivos.list_active"))
    if remesa.estado == "CANCELADO" and (current_user.can_admin(MODULO) or ROL_SOLICITANTE in current_user_roles):
        mostrar_secciones["boton_pasar_historial"] = True

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
                filtros=json.dumps({"remesa_id": remesa.id}),
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
                filtros=json.dumps({"remesa_id": remesa.id}),
                archivistas=archivistas,
            )
        if ROL_ARCHIVISTA in current_user_roles:
            return render_template(
                "arc_remesas/detail_archivista.jinja2",
                remesa=remesa,
                mostrar_secciones=mostrar_secciones,
                estado_text=estado_text,
                filtros=json.dumps({"remesa_id": remesa.id}),
            )

    if remesa.estado == "RECHAZADO":
        mostrar_secciones["rechazo"] = True
        if ROL_SOLICITANTE in current_user_roles:
            if not remesa.esta_archivado:
                mostrar_secciones["boton_pasar_historial"] = True

    # Por defecto mostramos solo los detalles de la remesa
    return render_template(
        "arc_remesas/detail.jinja2",
        remesa=remesa,
        mostrar_secciones=mostrar_secciones,
        estado_text=estado_text,
        filtros=json.dumps({"remesa_id": remesa.id}),
    )


@arc_remesas.route("/arc_remesas/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Remesa"""

    form = ArcRemesaNewForm()
    if form.validate_on_submit():
        if form.anio.data < 1950 or form.anio.data > date.today().year:
            flash(f"El año se encuentra fuera de un rango permitido 1950-{date.today().year}.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
            flash(f"Solo se pueden crear nuevas remesas por el Administrador o {ROL_SOLICITANTE}.", "warning")
        else:
            remesa = ArcRemesa(
                autoridad=current_user.autoridad,
                esta_archivado=False,
                anio=int(form.anio.data),
                num_oficio=safe_string(form.num_oficio.data),
                estado="PENDIENTE",
            )
            remesa.save()
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


@arc_remesas.route("/arc_remesas/editar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(remesa_id):
    """Editar Remesa"""


@arc_remesas.route("/arc_remesas/enviar/<int:remesa_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def send(remesa_id):
    """Enviar Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede enviar remesas el ROL de {ROL_SOLICITANTE}.", "warning")
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

    flash("La Remesa ha sido enviada correctamente.", "success")
    return redirect(url_for("arc_archivos.list_active"))


@arc_remesas.route("/arc_remesas/agregar_documento/<int:documento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def add_document(documento_id):
    """Añadir documento a Remesa"""

    # Validar Permisos
    if not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede editar remesas el ROL de {ROL_SOLICITANTE}.", "warning")
        return redirect("arc_documentos.list_active")

    # Validar Documento
    documento = ArcDocumento.query.get_or_404(documento_id)
    if documento.estatus != "A":
        flash("El documento seleccionado está eliminado.", "warning")
        return redirect("arc_documentos.list_active")
    elif documento.ubicacion != "JUZGADO":
        flash("El documento se encuentra en una ubicación diferente a JUZGADO.", "warning")
        return redirect("arc_documentos.list_active")
    # Buscar si el documento ya está en otra remesa pendiente
    documento_en_otra_remesa = ArcRemesaDocumento.query
    documento_en_otra_remesa = documento_en_otra_remesa.filter_by(arc_documento_id=documento_id).first()
    if documento_en_otra_remesa:
        if documento_en_otra_remesa.arc_remesa.estado not in ("CANCELADO", "ARCHIVADO"):
            flash(f"Este documento ya está asignado a la remesa [{documento_en_otra_remesa.arc_remesa.id}] que se encuentra en proceso.", "warning")
            return redirect(url_for("arc_documentos.detail", documento_id=documento_id))
        if documento_en_otra_remesa.arc_remesa.estatus != "A":
            flash("Esta Remesa está eliminada.", "warning")
            return redirect("arc_documentos.list_active")

    # Validar el Formulario
    form = ArcRemesaAddDocumentForm()
    if form.validate_on_submit():
        # Validar la Remesa
        remesa = ArcRemesa.query.get_or_404(form.remesas.data.id)
        if remesa.autoridad_id != current_user.autoridad.id:
            flash("La remesa NO pertenece a su Autoridad.", "warning")
        elif remesa.estado != "PENDIENTE":
            flash("La remesa NO tiene un estado de PENDIENTE.", "warning")
        elif remesa.esta_archivado:
            flash("La remesa se encuentra ARCHIVADA, ya no puede ser modificada.", "warning")
        elif remesa.estatus != "A":
            flash("La remesa está eliminada.", "warning")
        else:
            documento_agregar = ArcRemesaDocumento(
                arc_documento=documento,
                arc_remesa=remesa,
                fojas=form.fojas.data,
                tipo=form.tipo.data,
                tiene_anomalia=form.tiene_anomalia.data,
                observaciones=safe_message(form.observaciones.data),
            )
            documento_agregar.save()
            flash(f"Se añadió el documento {documento.id} a la remesa {remesa.id}, correctamente.", "success")
            return redirect(url_for("arc_remesas.detail", remesa_id=remesa.id))

    # Datos sugeridos para el formulario
    form.fojas.data = documento.fojas
    form.tipo.data = documento.tipo_juzgado

    return render_template("arc_remesas/add_document.jinja2", documento=documento, form=form)


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
            remesa.rechazo = safe_message(form.observaciones.data)
            remesa.estado = "RECHAZADO"
            remesa.save()
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
    if remesa.estado not in ["CANCELADO", "RECHAZADO", "ARCHIVADO"]:
        flash("No puede pasar al historial una remesa en este estado.", "warning")
    elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
        flash(f"Solo puede pasar al historial el ROL de {ROL_SOLICITANTE}.", "warning")
    else:
        remesa.esta_archivado = True
        remesa.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Remesa pasada al Historial {remesa.id}"),
            url=url_for("arc_archivos.list_active"),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("arc_remesas.detail", remesa_id=remesa_id))
