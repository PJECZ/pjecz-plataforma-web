"""
CID Procedimientos, vistas
"""
import json
from delta import html
from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from wtforms.fields.core import StringField

from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_procedimientos.forms import CIDProcedimientoForm, CIDProcedimientoAcceptRejectForm
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.models import Usuario

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")

MODULO = "CID PROCEDIMIENTOS"


@cid_procedimientos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_procedimientos.route("/cid_procedimientos")
def list_authorized():
    """Listado de Procedimientos autorizados"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=CIDProcedimiento.query.filter_by(seguimiento="AUTORIZADO").filter_by(estatus="A").all(),
        titulo="Procedimientos autorizados",
        estatus="A",
    )


@cid_procedimientos.route("/cid_procedimientos/propios")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_owned():
    """Listado de Procedimientos propios"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=CIDProcedimiento.query.filter(CIDProcedimiento.usuario == current_user).filter_by(estatus="A").all(),
        titulo="Procedimientos propios",
        estatus="A",
    )


@cid_procedimientos.route("/cid_procedimientos/activos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_active():
    """Listado de TODOS los Procedimientos activos"""
    if current_user.can_admin(MODULO):
        cid_procedimientos_activos = CIDProcedimiento.query.filter_by(estatus="A").all()
    else:
        cid_procedimientos_activos = CIDProcedimiento.query.filter_by(usuario_id=current_user.id).filter_by(estatus="A").all()
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=cid_procedimientos_activos,
        titulo="Todos los procedimientos",
        estatus="A",
    )


@cid_procedimientos.route("/cid_procedimientos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de TODOS los Procedimientos inactivos"""
    if current_user.can_admin(MODULO):
        cid_procedimientos_inactivos = CIDProcedimiento.query.filter_by(estatus="B").all()
    else:
        cid_procedimientos_inactivos = CIDProcedimiento.query.filter_by(usuario_id=current_user.id).filter_by(estatus="B").all()
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=cid_procedimientos_inactivos,
        titulo="Todos los procedimientos inactivos",
        estatus="B",
    )


@cid_procedimientos.route("/cid_procedimientos/<int:cid_procedimiento_id>")
def detail(cid_procedimiento_id):
    """Detalle de un CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    cid_formatos = CIDFormato.query.filter(CIDFormato.procedimiento == cid_procedimiento).filter(CIDFormato.estatus == "A").order_by(CIDFormato.id).all()
    return render_template(
        "cid_procedimientos/detail.jinja2",
        cid_procedimiento=cid_procedimiento,
        firma_al_vuelo=cid_procedimiento.elaborar_firma(),
        objetivo=str(html.render(cid_procedimiento.objetivo["ops"])),
        alcance=str(html.render(cid_procedimiento.alcance["ops"])),
        documentos=str(html.render(cid_procedimiento.documentos["ops"])),
        definiciones=str(html.render(cid_procedimiento.definiciones["ops"])),
        responsabilidades=str(html.render(cid_procedimiento.responsabilidades["ops"])),
        desarrollo=str(html.render(cid_procedimiento.desarrollo["ops"])),
        registros=cid_procedimiento.registros,
        control_cambios=cid_procedimiento.control_cambios,
        cid_formatos=cid_formatos,
    )


@cid_procedimientos.route("/cid_procedimientos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo CID Procedimiento"""
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        elaboro = form.elaboro_email.data
        if elaboro is None:
            elaboro_nombre = ""
            elaboro_email = ""
        else:
            elaboro_nombre = elaboro.nombre
            elaboro_email = elaboro.email
        reviso = form.reviso_email.data
        if reviso is None:
            reviso_nombre = ""
            reviso_email = ""
        else:
            reviso_nombre = reviso.nombre
            reviso_email = reviso.email
        aprobo = form.aprobo_email.data
        if aprobo is None:
            aprobo_nombre = ""
            aprobo_email = ""
        else:
            aprobo_nombre = aprobo.nombre
            aprobo_email = aprobo.email
        registros_data = form.registros.data
        if registros_data is None:
            registros = ""
        else:
            registros = registros_data
        control = form.control_cambios.data
        if control is None:
            control_cambios = ""
        else:
            control_cambios = control
        cid_procedimiento = CIDProcedimiento(
            usuario=current_user,
            titulo_procedimiento=safe_string(form.titulo_procedimiento.data),
            codigo=form.codigo.data,
            revision=form.revision.data,
            fecha=form.fecha.data,
            objetivo=form.objetivo.data,
            alcance=form.alcance.data,
            documentos=form.documentos.data,
            definiciones=form.definiciones.data,
            responsabilidades=form.responsabilidades.data,
            desarrollo=form.desarrollo.data,
            registros=registros,
            elaboro_nombre=elaboro_nombre,
            elaboro_puesto=form.elaboro_puesto.data,
            elaboro_email=elaboro_email,
            reviso_nombre=reviso_nombre,
            reviso_puesto=form.reviso_puesto.data,
            reviso_email=reviso_email,
            aprobo_nombre=aprobo_nombre,
            aprobo_puesto=form.aprobo_puesto.data,
            aprobo_email=aprobo_email,
            control_cambios=control_cambios,
            cadena=0,
            seguimiento="EN ELABORACION",
            seguimiento_posterior="EN ELABORACION",
            anterior_id=0,
            firma="",
            archivo="",
            url="",
        )
        cid_procedimiento.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Procedimiento {cid_procedimiento.titulo_procedimiento}"),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("cid_procedimientos/new.jinja2", form=form, help_quill=help_quill("new"))


@cid_procedimientos.route("/cid_procedimientos/edicion/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cid_procedimiento_id):
    """Editar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede editarlo
    if cid_procedimiento.seguimiento not in ["EN ELABORACION", "EN REVISION", "EN AUTORIZACION"]:
        flash(f"No puede editar porque su seguimiento es {cid_procedimiento.seguimiento}.")
        redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        elaboro = form.elaboro_email.data
        if elaboro is None:
            elaboro_nombre = ""
            elaboro_email = ""
        else:
            elaboro_nombre = elaboro.nombre
            elaboro_email = elaboro.email
        reviso = form.reviso_email.data
        if reviso is None:
            reviso_nombre = ""
            reviso_email = ""
        else:
            reviso_nombre = reviso.nombre
            reviso_email = reviso.email
        aprobo = form.aprobo_email.data
        if aprobo is None:
            aprobo_nombre = ""
            aprobo_email = ""
        else:
            aprobo_nombre = aprobo.nombre
            aprobo_email = aprobo.email
        registros_d = form.registros.data
        if registros_d is None:
            registros = ""
        else:
            registros = registros_d
        control = form.control_cambios.data
        if control is None:
            control_cambios = ""
        else:
            control_cambios = control
        cid_procedimiento.titulo_procedimiento = safe_string(form.titulo_procedimiento.data)
        cid_procedimiento.codigo = form.codigo.data
        cid_procedimiento.revision = form.revision.data
        cid_procedimiento.fecha = form.fecha.data
        cid_procedimiento.objetivo = form.objetivo.data
        cid_procedimiento.alcance = form.alcance.data
        cid_procedimiento.documentos = form.documentos.data
        cid_procedimiento.definiciones = form.definiciones.data
        cid_procedimiento.responsabilidades = form.responsabilidades.data
        cid_procedimiento.desarrollo = form.desarrollo.data
        cid_procedimiento.registros = registros
        cid_procedimiento.elaboro_nombre = elaboro_nombre
        cid_procedimiento.elaboro_puesto = form.elaboro_puesto.data
        cid_procedimiento.elaboro_email = elaboro_email
        cid_procedimiento.reviso_nombre = reviso_nombre
        cid_procedimiento.reviso_puesto = form.reviso_puesto.data
        cid_procedimiento.reviso_email = reviso_email
        cid_procedimiento.aprobo_nombre = aprobo_nombre
        cid_procedimiento.aprobo_puesto = form.aprobo_puesto.data
        cid_procedimiento.aprobo_email = aprobo_email
        cid_procedimiento.control_cambios = control_cambios
        cid_procedimiento.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Definir los valores de los campos del formulario
    form.titulo_procedimiento.data = cid_procedimiento.titulo_procedimiento
    form.codigo.data = cid_procedimiento.codigo
    form.revision.data = cid_procedimiento.revision
    form.fecha.data = cid_procedimiento.fecha
    form.objetivo.data = cid_procedimiento.objetivo
    form.alcance.data = cid_procedimiento.alcance
    form.documentos.data = cid_procedimiento.documentos
    form.definiciones.data = cid_procedimiento.definiciones
    form.responsabilidades.data = cid_procedimiento.responsabilidades
    form.desarrollo.data = cid_procedimiento.desarrollo
    form.registros.data = cid_procedimiento.registros
    form.elaboro_nombre.data = cid_procedimiento.elaboro_nombre
    form.elaboro_puesto.data = cid_procedimiento.elaboro_puesto
    form.elaboro_email.data = cid_procedimiento.elaboro_email
    form.reviso_nombre.data = cid_procedimiento.reviso_nombre
    form.reviso_puesto.data = cid_procedimiento.reviso_puesto
    form.reviso_email.data = cid_procedimiento.reviso_email
    form.aprobo_nombre.data = cid_procedimiento.aprobo_nombre
    form.aprobo_puesto.data = cid_procedimiento.aprobo_puesto
    form.aprobo_email.data = cid_procedimiento.aprobo_email
    form.control_cambios.data = cid_procedimiento.control_cambios
    # Para cargar el contenido de los QuillJS hay que convertir a JSON válido (por ejemplo, cambia True por true)
    objetivo_json = json.dumps(cid_procedimiento.objetivo)
    alcance_json = json.dumps(cid_procedimiento.alcance)
    documentos_json = json.dumps(cid_procedimiento.documentos)
    definiciones_json = json.dumps(cid_procedimiento.definiciones)
    responsabilidades_json = json.dumps(cid_procedimiento.responsabilidades)
    desarrollo_json = json.dumps(cid_procedimiento.desarrollo)
    registros_json = json.dumps(cid_procedimiento.registros)
    control_cambios_json = json.dumps(cid_procedimiento.control_cambios)
    return render_template(
        "cid_procedimientos/edit.jinja2",
        form=form,
        cid_procedimiento=cid_procedimiento,
        objetivo_json=objetivo_json,
        alcance_json=alcance_json,
        documentos_json=documentos_json,
        definiciones_json=definiciones_json,
        responsabilidades_json=responsabilidades_json,
        desarrollo_json=desarrollo_json,
        registros_json=registros_json,
        control_cambios_json=control_cambios_json,
        help_quill=help_quill("edit"),
    )


def validate_json_quill_not_empty(data):
    """Validar que un JSON de Quill no esté vacío"""
    if not isinstance(data, dict):
        return False
    if not "ops" in data:
        return False
    try:
        if data["ops"][0]["insert"].strip() == "":
            return False
        return True
    except KeyError:
        return False


@cid_procedimientos.route("/cid_procedimientos/firmar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def sign_for_maker(cid_procedimiento_id):
    """Firmar"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.usuario_id != current_user.id:
        abort(403)  # Acceso no autorizado, solo el propietario puede firmarlo
    # Validar objetivo
    objetivo_es_valido = validate_json_quill_not_empty(cid_procedimiento.objetivo)
    # Validar alcance
    alcance_es_valido = validate_json_quill_not_empty(cid_procedimiento.alcance)
    # Validar documentos
    documentos_es_valido = validate_json_quill_not_empty(cid_procedimiento.documentos)
    # Validar definiciones
    definiciones_es_valido = validate_json_quill_not_empty(cid_procedimiento.definiciones)
    # Validar responsabilidades
    responsabilidades_es_valido = validate_json_quill_not_empty(cid_procedimiento.responsabilidades)
    # Validar desarrollo
    desarrollo_es_valido = validate_json_quill_not_empty(cid_procedimiento.desarrollo)
    # Validar registros
    registros_es_valido = cid_procedimiento.registros
    # Validar control_cambios
    control_cambios_es_valido = cid_procedimiento.control_cambios

    # Validar elaboro
    elaboro_es_valido = False
    if cid_procedimiento.elaboro_email != "":
        elaboro = Usuario.query.filter_by(email=cid_procedimiento.elaboro_email).first()
        elaboro_es_valido = elaboro is not None  # TODO: Validar que tenga el rol SICGD DUENO DE PROCESO
    # Validar reviso
    reviso_es_valido = False
    if cid_procedimiento.reviso_email != "":
        reviso = Usuario.query.filter_by(email=cid_procedimiento.reviso_email).first()
        reviso_es_valido = reviso is not None  # TODO: Validar que tenga el rol SICGD DIRECTOR O JEFE
    # Validar autorizo
    aprobo_es_valido = False
    if cid_procedimiento.aprobo_email != "":
        aprobo = Usuario.query.filter_by(email=cid_procedimiento.aprobo_email).first()
        aprobo_es_valido = aprobo is not None  # TODO: Validar que tenga el rol SICGD DIRECTOR O JEFE
    # Poner barreras para prevenir que se firme si está incompleto
    if cid_procedimiento.firma != "":
        flash("Este procedimiento ya ha sido firmado.", "warning")
    elif not objetivo_es_valido:
        flash("Objetivo no pasa la validación.", "warning")
    elif not alcance_es_valido:
        flash("Alcance no pasa la validación.", "warning")
    elif not documentos_es_valido:
        flash("Documentos no pasa la validación.", "warning")
    elif not definiciones_es_valido:
        flash("Definiciones no pasa la validación.", "warning")
    elif not responsabilidades_es_valido:
        flash("Responsabilidades no pasa la validación.", "warning")
    elif not desarrollo_es_valido:
        flash("Desarrollo no pasa la validación.", "warning")
    elif not registros_es_valido:
        flash("Registros no pasa la validación.", "warning")
    elif not control_cambios_es_valido:
        flash("Control de Cambios no pasa la validación.", "warning")
    elif not elaboro_es_valido:
        flash("Quien elabora no pasa la validación.", "warning")
    elif not reviso_es_valido:
        flash("Quien revisa no pasa la validación.", "warning")
    elif not aprobo_es_valido:
        flash("Quien aprueba no pasa la validación.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="cid_procedimientos.tasks.crear_pdf",
            descripcion=f"Crear archivo PDF de {cid_procedimiento.titulo_procedimiento}",
            usuario_id=current_user.id,
            cid_procedimiento_id=cid_procedimiento.id,
            accept_reject_url=url_for("cid_procedimientos.accept_reject", cid_procedimiento_id=cid_procedimiento.id),
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))


@cid_procedimientos.route("/cid_procedimientos/aceptar_rechazar/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def accept_reject(cid_procedimiento_id):
    """Aceptar o Rechazar un Procedimiento"""
    original = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    # Validar que NO haya sido eliminado
    if original.estatus != "A":
        flash("Este procedimiento no es activo.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    # Validar que este procedimiento este elaborado o revisado
    if not original.seguimiento in ["ELABORADO", "REVISADO"]:
        flash("Este procedimiento no puede ser aceptado.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    # Validar que NO haya sido YA aceptado
    if original.seguimiento_posterior in ["EN REVISION", "EN AUTORIZACION"]:
        flash("Este procedimiento ya fue aceptado.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    form = CIDProcedimientoAcceptRejectForm()
    if form.validate_on_submit():
        # Si fue aceptado
        if form.aceptar.data is True:
            # Crear un nuevo registro
            nuevo = CIDProcedimiento(
                titulo_procedimiento=safe_string(original.titulo_procedimiento),
                codigo=original.codigo,
                revision=original.revision,
                fecha=original.fecha,
                objetivo=original.objetivo,
                alcance=original.alcance,
                documentos=original.documentos,
                definiciones=original.definiciones,
                responsabilidades=original.responsabilidades,
                desarrollo=original.desarrollo,
                registros=original.registros,
                elaboro_nombre=original.elaboro_nombre,
                elaboro_puesto=original.elaboro_puesto,
                elaboro_email=original.elaboro_email,
                reviso_nombre=original.reviso_nombre,
                reviso_puesto=original.reviso_puesto,
                reviso_email=original.reviso_email,
                aprobo_nombre=original.aprobo_nombre,
                aprobo_puesto=original.aprobo_puesto,
                aprobo_email=original.aprobo_email,
                control_cambios=original.control_cambios,
            )
            nuevo.cadena = original.cadena + 1
            # Si este procedimiento fue elaborado, sigue revisarlo
            if original.seguimiento == "ELABORADO":
                # Validar el usuario que revisara
                usuario = Usuario.query.filter_by(email=original.reviso_email).first()
                if usuario is None:
                    flash(f"No fue encontrado el usuario con e-mail {original.reviso_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
                nuevo.seguimiento = "EN REVISION"
                nuevo.seguimiento_posterior = "EN REVISION"
                nuevo.usuario = usuario
            # Si este procedimiento fue revisado, sigue autorizarlo
            if original.seguimiento == "REVISADO":
                usuario = Usuario.query.filter_by(email=original.aprobo_email).first()
                if usuario is None:
                    flash(f"No fue encontrado el usuario con e-mail {original.aprobo_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
                nuevo.seguimiento = "EN AUTORIZACION"
                nuevo.seguimiento_posterior = "EN AUTORIZACION"
                nuevo.usuario = usuario
            # Guardar nuevo procedimiento
            nuevo.anterior_id = original.id
            nuevo.firma = ""
            nuevo.archivo = ""
            nuevo.url = ""
            nuevo.save()
            # Actualizar el anterior
            if original.seguimiento == "ELABORADO":
                # Cambiar el seguimiento posterior del procedimiento elaborado
                anterior = CIDProcedimiento.query.get(cid_procedimiento_id)
                anterior.seguimiento_posterior = "EN REVISION"
                anterior.save()
            if original.seguimiento == "REVISADO":
                # Cambiar el seguimiento posterior del procedimiento revisado
                anterior = CIDProcedimiento.query.get(cid_procedimiento_id)
                anterior.seguimiento_posterior = "EN AUTORIZACION"
                anterior.save()
            # Bitacora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Aceptado el Procedimiento {nuevo.titulo_procedimiento}."),
                url=url_for("cid_procedimientos.detail", cid_procedimiento_id=nuevo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        # Fue rechazado
        if form.rechazar.data is True:
            # Preguntar porque fue rechazado
            flash("Usted ha rechazado revisar/autorizar este procedimiento.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    form.titulo_procedimiento.data = original.titulo_procedimiento
    form.codigo.data = original.codigo
    form.revision.data = original.revision
    form.seguimiento.data = original.seguimiento
    form.seguimiento_posterior.data = original.seguimiento_posterior
    form.elaboro_nombre.data = original.elaboro_nombre
    form.reviso_nombre.data = original.reviso_nombre
    form.url.data = original.url
    return render_template("cid_procedimientos/accept_reject.jinja2", form=form, cid_procedimiento=original)


@cid_procedimientos.route("/cid_procedimientos/eliminar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(cid_procedimiento_id):
    """Eliminar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede eliminarlo
    if not (current_user.can_admin(MODULO) or cid_procedimiento.seguimiento in ["EN ELABORACION", "EN REVISION", "EN AUTORIZACION"]):
        flash(f"No puede eliminarlo porque su seguimiento es {cid_procedimiento.seguimiento}.")
    elif cid_procedimiento.estatus == "A":
        if cid_procedimiento.seguimiento == "EN ELABORACION":
            cid_procedimiento.seguimiento = "CANCELADO POR ELABORADOR"
        elif cid_procedimiento.seguimiento == "EN REVISION":
            cid_procedimiento.seguimiento = "CANCELADO POR REVISOR"
        elif cid_procedimiento.seguimiento == "EN AUTORIZACION":
            cid_procedimiento.seguimiento = "CANCELADO POR AUTORIZADOR"
        cid_procedimiento.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


@cid_procedimientos.route("/cid_procedimientos/recuperar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(cid_procedimiento_id):
    """Recuperar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede recuperarlo
    if not (current_user.can_admin(MODULO) or cid_procedimiento.seguimiento in ["CANCELADO POR ELABORADOR", "CANCELADO POR REVISOR", "CANCELADO POR AUTORIZADOR"]):
        flash(f"No puede recuperarlo porque su seguimiento es {cid_procedimiento.seguimiento}.")
    elif cid_procedimiento.estatus == "B":
        if cid_procedimiento.seguimiento == "CANCELADO POR ELABORADOR":
            cid_procedimiento.seguimiento = "EN ELABORACION"
        elif cid_procedimiento.seguimiento == "CANCELADO POR REVISOR":
            cid_procedimiento.seguimiento = "EN REVISION"
        elif cid_procedimiento.seguimiento == "CANCELADO POR AUTORIZADOR":
            cid_procedimiento.seguimiento = "EN AUTORIZACION"
        cid_procedimiento.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


def help_quill(seccion: str):
    """Cargar archivo de ayuda"""
    archivo_ayuda = open("plataforma_web/static/json/help/quill_help.json", "r")
    data = json.load(archivo_ayuda)
    archivo_ayuda.close()
    return render_template("quill_help.jinja2", titulo=data["titulo"], descripcion=data["descripcion"], secciones=data["secciones"], seccion_id=seccion)
