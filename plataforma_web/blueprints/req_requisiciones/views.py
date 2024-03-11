"""
Requisiciones Requisiciones, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.req_requisiciones.models import ReqRequisicion

MODULO = "REQ REQUISICIONES"

req_requisiciones = Blueprint("req_requisiciones", __name__, template_folder="templates")


@req_requisiciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@req_requisiciones.route("/req_requisiciones")
def list_active():
    """Listado de Requisiciones activos"""
    return render_template(
        "req_requisiciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Requisiciones",
        estatus="A",
    )
"""
Requisiciones Requisiciones, vistas
"""

from datetime import datetime
import json
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.req_requisiciones.models import ReqRequisicion
from plataforma_web.blueprints.req_requisiciones.forms import ReqRequisicionCancel2RequestForm, ReqRequisicionNewForm, ReqRequisicionStep2RequestForm, ReqRequisicionStep3AuthorizeForm, ReqRequisicionStep4ReviewForm
from plataforma_web.blueprints.req_requisiciones.forms import ArticulosForm
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.req_catalogos.models import ReqCatalogo
from plataforma_web.blueprints.req_requisiciones_registros.models import ReqRequisicionRegistro
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import db

MODULO = "REQ REQUISICIONES"

# Roles que deben estar en la base de datos
ROL_ASISTENTES = "REQUISICIONES ASISTENTES"
ROL_SOLICITANTES = "REQUISICIONES SOLICITANTES"
ROL_AUTORIZANTES = "REQUISICIONES AUTORIZANTES"
ROL_REVISANTES = "REQUISICIONES REVISANTES"

ROLES_PUEDEN_VER = (ROL_SOLICITANTES, ROL_AUTORIZANTES, ROL_REVISANTES, ROL_ASISTENTES)
ROLES_PUEDEN_IMPRIMIR = (ROL_SOLICITANTES, ROL_AUTORIZANTES, ROL_REVISANTES, ROL_ASISTENTES)

req_requisiciones = Blueprint("req_requisiciones", __name__, template_folder="templates")


@req_requisiciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@req_requisiciones.route("/req_requisiciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Requisiciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ReqRequisicion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "glosa" in request.form:
        consulta = consulta.filter(ReqRequisicion.glosa.contains(safe_string(request.form["glosa"], to_uppercase=False)))
    if "observaciones" in request.form:
        consulta = consulta.filter(ReqRequisicion.observaciones.contains(safe_string(request.form["observaciones"], to_uppercase=True)))
    registros = consulta.order_by(ReqRequisicion.id).offset(start).limit(rows_per_page).all()

    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "estado": resultado.estado,
                "oficina": resultado.autoridad.descripcion,
                "creado": resultado.usuario.nombre,
                "fecha": resultado.fecha,
                "glosa": resultado.glosa,
                "detalle": {
                    "consecutivo": resultado.id,
                    "url": url_for("req_requisiciones.detail", req_requisicion_id=resultado.id),
                },
                "observaciones": resultado.observaciones,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@req_requisiciones.route("/req_requisiciones")
def list_active():
    """Listado de Requisiciones activos"""

    # Si es administrador puede ver TODAS las requisiciones
    if current_user.can_admin(MODULO):
        return render_template(
            "req_requisiciones/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Administrar las Requisiciones",
            estatus="A",
        )
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es asistente, mostrar TODAS las Requisiciones de su oficina
    if ROL_ASISTENTES in current_user_roles:
        return render_template(
            "req_requisiciones/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Requisiciones de mi oficina",
            estatus="A",
        )
    # Si es autorizante, mostrar Requisiciones por Autorizar
    if ROL_AUTORIZANTES in current_user_roles:
        return render_template(
            "req_requisiciones/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "SOLICITADO"}),
            titulo="Requisiciones Solicitadas (por autorizar)",
            estatus="A",
        )
    # Si es solicitante, mostrar Requisiciones por Solicitar
    if ROL_SOLICITANTES in current_user_roles:
        return render_template(
            "req_requisiciones/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "CREADO"}),
            titulo="Requisiciones Creadas (por solicitar)",
            estatus="A",
        )
    # Mostrar Mis Requisiciones
    return render_template(
        "req_requisiciones/list.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
        titulo="Mis Requisiciones",
        estatus="A",
    )


@req_requisiciones.route("/req_requisiciones/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Requisiciones inactivas"""
    return render_template(
        "req_requisiciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Listado de requisiciones inactivas",
        estatus="B",
    )


@req_requisiciones.route("/req_requisiciones/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Requisiciones nueva"""
    form = ReqRequisicionNewForm()
    form.area.choices = [("", "")] + [(a.id, a.descripcion) for a in Autoridad.query.order_by("descripcion")]
    form.codigoTmp.choices = [("", "")] + [(c.id, c.codigo + " - " + c.descripcion) for c in ReqCatalogo.query.order_by("descripcion")]
    form.claveTmp.choices = [("", "")] + [("INS", "INSUFICIENCIA")] + [("REP", "REPOSICION DE BIENES")] + [("OBS", "OBSOLESENCIA")] + [("AMP", "AMPLIACION COBERTURA DEL SERVICIO")] + [("NUE", "NUEVO PROYECTO")]
    if form.validate_on_submit():
        # Guardar requisicion
        req_requisicion = ReqRequisicion(
            usuario=current_user,
            autoridad_id=form.area.data,
            estado="CREADO",
            observaciones=safe_string(form.observaciones.data, max_len=256, to_uppercase=True, save_enie=True),
            justificacion=safe_string(form.justificacion.data, max_len=1024, to_uppercase=True, save_enie=True),
            fecha=datetime.now(),
            consecutivo=safe_string(form.gasto.data, to_uppercase=True, save_enie=True),
            glosa=form.glosa.data,
            programa=safe_string(form.programa.data, to_uppercase=True, save_enie=True),
            fuente=safe_string(form.fuente.data, to_uppercase=True, save_enie=True),
            area=safe_string(form.areaFinal.data, to_uppercase=True, save_enie=True),
            fecha_requerida=form.fechaRequerida.data,
        )
        req_requisicion.save()
        # Guardar los registros de la requisición
        for registros in form.articulos:
            if registros.codigo.data != None:
                req_requisicion_registro = ReqRequisicionRegistro(
                    req_requisicion_id=req_requisicion.id,
                    req_catalogo_id=registros.codigo.data,
                    clave=registros.clave.data,
                    cantidad=registros.cantidad.data,
                    detalle=registros.detalle.data,
                )
                req_requisicion_registro.save()

        # Guardar en la bitacora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Requisicion creada {req_requisicion.observaciones}"),
            url=url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("req_requisiciones/new.jinja2", titulo="Requisicion nueva", form=form)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>")
def detail(req_requisicion_id):
    """Detalle de una Requisicion"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    articulos = db.session.query(ReqRequisicionRegistro, ReqCatalogo).filter_by(req_requisicion_id=req_requisicion_id).join(ReqCatalogo).all()
    usuario = Usuario.query.get_or_404(req_requisicion.usuario_id)
    autoridad = Autoridad.query.get_or_404(req_requisicion.autoridad_id)
    return render_template("req_requisiciones/detail.jinja2", req_requisicion=req_requisicion, req_requisicion_registro=articulos, usuario=usuario, autoridad=autoridad)


@req_requisiciones.route("/req_requisiciones/buscarRegistros/", methods=["GET"])
def buscarRegistros():
    args = request.args
    registro = ReqCatalogo.query.get_or_404(args.get("req_catalogo_id"))
    return ReqCatalogo.object_as_dict(registro)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/solicitar", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_2_request(req_requisicion_id):
    """Formulario Requisiciones (step 2 request) Solicitar"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    puede_firmarlo = True
    # Validar que sea activo
    if req_requisicion.estatus != "A":
        flash("La Requisición esta eliminada", "warning")
        puede_firmarlo = False
    # Validar el estado
    if req_requisicion.estado != "CREADO":
        flash("La Requisición no esta en estado CREADO", "warning")
        puede_firmarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_firmarlo = False
    if ROL_SOLICITANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para solicitar una requisición", "warning")
        puede_firmarlo = False
    # Si no puede solicitarla, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Si viene el formulario
    form = ReqRequisicionStep2RequestForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.req_requisiciones.tasks.solicitar",
            req_requisicion_id=req_requisicion.id,
            usuario_id=current_user.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Mostrar formulario
    form.solicito_nombre.data = current_user.nombre
    form.solicito_puesto.data = current_user.puesto
    form.solicito_email.data = current_user.email
    return render_template("req_requisiciones/step_2_request.jinja2", form=form, req_requisicion=req_requisicion)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/cancelar_solicitado", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel_2_request(req_requisicion_id):
    """Formulario Requisicion (cancel 2 request) Cancelar solicitado"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    puede_cancelarlo = True
    # Validar que sea activo
    if req_requisicion.estatus != "A":
        flash("La requisición esta cancelada", "warning")
        puede_cancelarlo = False
    # Validar el estado
    if req_requisicion.estado != "SOLICITADO":
        flash("La requisición no esta en estado SOLICITADO", "warning")
        puede_cancelarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_cancelarlo = False
    if ROL_SOLICITANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para cancelar un una requisición solicitada", "warning")
        puede_cancelarlo = False
    if req_requisicion.solicito_email != current_user.email:
        flash("Usted no es el solicitante de esta requisición", "warning")
        puede_cancelarlo = False
    # Si no puede cancelarlo, redireccionar a la pagina de detalle
    if not puede_cancelarlo:
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Si viene el formulario
    form = ReqRequisicionCancel2RequestForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.req_requisiciones.tasks.cancelar_solicitar",
            req_requisicion_id=req_requisicion.id,
            contrasena=form.contrasena.data,
            motivo=form.motivo.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Mostrar formulario
    form.solicito_nombre.data = current_user.nombre
    form.solicito_puesto.data = current_user.puesto
    form.solicito_email.data = current_user.email
    return render_template("req_requisiciones/cancel_2_request.jinja2", form=form, req_requisicion=req_requisicion)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/autorizar", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_3_authorize(req_requisicion_id):
    """Formulario Requisiciones (step 3 authorize) Autorizar"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    puede_firmarlo = True
    # Validar que sea activo
    if req_requisicion.estatus != "A":
        flash("La Requisición esta eliminada", "warning")
        puede_firmarlo = False
    # Validar el estado
    if req_requisicion.estado != "SOLICITADO":
        flash("La Requisición no esta en estado SOLICITADO", "warning")
        puede_firmarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_firmarlo = False
    if ROL_AUTORIZANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para AUTORIZAR una requisición", "warning")
        puede_firmarlo = False
    # Si no puede autorizarla, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Si viene el formulario
    form = ReqRequisicionStep3AuthorizeForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.req_requisiciones.tasks.autorizar",
            req_requisicion_id=req_requisicion.id,
            usuario_id=current_user.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Mostrar formulario
    form.autorizo_nombre.data = current_user.nombre
    form.autorizo_puesto.data = current_user.puesto
    form.autorizo_email.data = current_user.email
    return render_template("req_requisiciones/step_3_authorize.jinja2", form=form, req_requisicion=req_requisicion)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/revisar", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_4_review(req_requisicion_id):
    """Formulario Requisiciones (step 4 review) Revisar"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    puede_firmarlo = True
    # Validar que sea activo
    if req_requisicion.estatus != "A":
        flash("La Requisición esta eliminada", "warning")
        puede_firmarlo = False
    # Validar el estado
    if req_requisicion.estado != "AUTORIZADO":
        flash("La Requisición no esta en estado AUTORIZADO", "warning")
        puede_firmarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_firmarlo = False
    if ROL_REVISANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para REVISAR una requisición", "warning")
        puede_firmarlo = False
    # Si no puede revisar la requisición, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Si viene el formulario
    form = ReqRequisicionStep4ReviewForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.req_requisiciones.tasks.revisar",
            req_requisicion_id=req_requisicion.id,
            usuario_id=current_user.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
    # Mostrar formulario
    form.reviso_nombre.data = current_user.nombre
    form.reviso_puesto.data = current_user.puesto
    form.reviso_email.data = current_user.email
    return render_template("req_requisiciones/step_4_review.jinja2", form=form, req_requisicion=req_requisicion)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/imprimir")
def detail_print(req_requisicion_id):
    """Impresion de la Requsición"""

    # Consultar el vale
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    articulos = db.session.query(ReqRequisicionRegistro, ReqCatalogo).filter_by(req_requisicion_id=req_requisicion_id).join(ReqCatalogo).all()
    usuario = Usuario.query.get_or_404(req_requisicion.usuario_id)

    # Determinar el sello digital y la URL de la firma electronica
    efirma_sello_digital = None
    efirma_url = None
    efirma_qr_url = None
    efirma_motivo = None

    # Si el estado es...
    if req_requisicion.estado == "SOLICITADO":
        efirma_sello_digital = req_requisicion.solicito_efirma_sello_digital
        efirma_url = req_requisicion.solicito_efirma_url
        efirma_qr_url = req_requisicion.solicito_efirma_qr_url
    elif req_requisicion.estado == "CANCELADO POR SOLICITANTE":
        efirma_sello_digital = req_requisicion.solicito_efirma_sello_digital
        efirma_url = req_requisicion.solicito_efirma_url
        efirma_qr_url = req_requisicion.solicito_efirma_qr_url
        efirma_motivo = req_requisicion.solicito_cancelo_motivo
    elif req_requisicion.estado == "AUTORIZADO":
        efirma_sello_digital = req_requisicion.autorizo_efirma_sello_digital
        efirma_url = req_requisicion.autorizo_efirma_url
        efirma_qr_url = req_requisicion.autorizo_efirma_qr_url
    elif req_requisicion.estado == "CANCELADO POR AUTORIZANTE":
        efirma_sello_digital = req_requisicion.autorizo_efirma_sello_digital
        efirma_url = req_requisicion.autorizo_efirma_url
        efirma_qr_url = req_requisicion.autorizo_efirma_qr_url
        efirma_motivo = req_requisicion.autorizo_cancelo_motivo

    # Validar que pueda verlo
    puede_imprimirlo = False

    # Si es administrador, puede imprimirlo
    if current_user.can_admin(MODULO):
        puede_imprimirlo = True

    # Si tiene uno de los roles que pueden imprimir y esta activo, puede imprimirlo
    if set(current_user.get_roles()).intersection(ROLES_PUEDEN_IMPRIMIR) and req_requisicion.estatus == "A":
        puede_imprimirlo = True

    # Si es el usuario que lo creo y esta activo, puede imprimirlo
    if req_requisicion.usuario_id == current_user.id and req_requisicion.estatus == "A":
        puede_imprimirlo = True

    # Si puede imprimirlo
    if puede_imprimirlo:
        # Cortar las lineas del sello digital insertando saltos de linea cada 40 caracteres
        if efirma_sello_digital is not None:
            efirma_sello_digital = "<br>".join([efirma_sello_digital[i : i + 40] for i in range(0, len(efirma_sello_digital), 40)])
        # Mostrar la plantilla para imprimir
        return render_template(
            "req_requisiciones/print.jinja2",
            req_requisicion=req_requisicion,
            req_requisicion_registro=articulos,
            usuario=usuario,
            efirma_sello_digital=efirma_sello_digital,
            efirma_url=efirma_url,
            efirma_qr_url=efirma_qr_url,
            efirma_motivo=efirma_motivo,
        )

    # No puede imprimirlo
    flash("No tiene permiso para imprimir la requisición", "warning")
    return redirect(url_for("req_requisiciones.list_active"))


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>/eliminar")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(req_requisicion_id):
    print("Inicia el proceso de borrado")
    """Eliminar Requisición"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    if req_requisicion.estatus == "A":
        puede_eliminarlo = False
        if current_user.can_admin(MODULO):
            puede_eliminarlo = True
        if req_requisicion.usuario == current_user and req_requisicion.estado == "CREADO":
            puede_eliminarlo = True
        if req_requisicion.solicito_email == current_user.email and req_requisicion.estado == "SOLICITADO":
            puede_eliminarlo = True
        if req_requisicion.autorizo_email == current_user.email and req_requisicion.estado == "AUTORIZADO":
            puede_eliminarlo = True
        if not puede_eliminarlo:
            flash("No tiene permisos para eliminar o tiene un estado particular", "warning")
            return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion_id))
        req_requisicion.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada Requisición {req_requisicion.justificacion}"),
            url=url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion.id))
