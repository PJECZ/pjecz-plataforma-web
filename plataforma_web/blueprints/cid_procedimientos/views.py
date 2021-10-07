"""
CID Procedimientos, vistas
"""
from delta import html
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.cid_procedimientos.forms import CIDProcedimientoForm, CIDProcedimientoAcceptRejectForm
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.models import Usuario

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")

MODULO = "ISO PROCEDIMIENTOS"


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
def list_owned():
    """Listado de Procedimientos propios"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=CIDProcedimiento.query.filter(CIDProcedimiento.usuario == current_user).filter_by(estatus="A").all(),
        titulo="Procedimientos propios",
        estatus="A",
    )


@cid_procedimientos.route("/cid_procedimientos/activos")
def list_active():
    """Listado de TODOS los Procedimientos activos"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=CIDProcedimiento.query.filter_by(estatus="A").all(),
        titulo="Todos los procedimientos",
        estatus="A",
    )


@cid_procedimientos.route("/cid_procedimientos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de TODOS los Procedimientos inactivos"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        cid_procedimientos=CIDProcedimiento.query.filter_by(estatus="B").all(),
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
        registros=str(html.render(cid_procedimiento.registros["ops"])),
        control_cambios=str(html.render(cid_procedimiento.control_cambios["ops"])),
        cid_formatos=cid_formatos,
    )


@cid_procedimientos.route("/cid_procedimientos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo CID Procedimiento"""
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        elaboro = form.elaboro_email.data
        reviso = form.reviso_email.data
        aprobo = form.aprobo_email.data
        cid_procedimiento = CIDProcedimiento(
            usuario=current_user,
            titulo_procedimiento=form.titulo_procedimiento.data,
            codigo=form.codigo.data,
            revision=form.revision.data,
            fecha=form.fecha.data,
            objetivo=form.objetivo.data,
            alcance=form.alcance.data,
            documentos=form.documentos.data,
            definiciones=form.definiciones.data,
            responsabilidades=form.responsabilidades.data,
            desarrollo=form.desarrollo.data,
            registros=form.registros.data,
            elaboro_nombre=elaboro.nombre,
            elaboro_puesto=form.elaboro_puesto.data,
            elaboro_email=elaboro.email,
            reviso_nombre=reviso.nombre,
            reviso_puesto=form.reviso_puesto.data,
            reviso_email=reviso.email,
            aprobo_nombre=aprobo.nombre,
            aprobo_puesto=form.aprobo_puesto.data,
            aprobo_email=aprobo.email,
            control_cambios=form.control_cambios.data,
            cadena=0,
            seguimiento="EN ELABORACION",
            seguimiento_posterior="EN ELABORACION",
            anterior_id=0,
            firma="",
            archivo="",
            url="",
        )
        cid_procedimiento.save()
        flash(f"Procedimiento {cid_procedimiento.titulo_procedimiento} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    return render_template("cid_procedimientos/new.jinja2", form=form)


@cid_procedimientos.route("/cid_procedimientos/edicion/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cid_procedimiento_id):
    """Editar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        cid_procedimiento.titulo_procedimiento = form.titulo_procedimiento.data
        cid_procedimiento.codigo = form.codigo.data
        cid_procedimiento.revision = form.revision.data
        cid_procedimiento.fecha = form.fecha.data
        cid_procedimiento.objetivo = form.objetivo.data
        cid_procedimiento.alcance = form.alcance.data
        cid_procedimiento.documentos = form.documentos.data
        cid_procedimiento.definiciones = form.definiciones.data
        cid_procedimiento.responsabilidades = form.responsabilidades.data
        cid_procedimiento.desarrollo = form.desarrollo.data
        cid_procedimiento.registros = form.registros.data
        cid_procedimiento.elaboro_nombre = form.elaboro_nombre.data
        cid_procedimiento.elaboro_puesto = form.elaboro_puesto.data
        cid_procedimiento.elaboro_email = form.elaboro_email.data
        cid_procedimiento.reviso_nombre = form.reviso_nombre.data
        cid_procedimiento.reviso_puesto = form.reviso_puesto.data
        cid_procedimiento.reviso_email = form.reviso_email.data
        cid_procedimiento.aprobo_nombre = form.aprobo_nombre.data
        cid_procedimiento.aprobo_puesto = form.aprobo_puesto.data
        cid_procedimiento.aprobo_email = form.aprobo_email.data
        cid_procedimiento.control_cambios = form.control_cambios.data
        cid_procedimiento.save()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
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
    return render_template("cid_procedimientos/edit.jinja2", form=form, cid_procedimiento=cid_procedimiento)


@cid_procedimientos.route("/cid_procedimientos/firmar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def sign_for_maker(cid_procedimiento_id):
    """Firmar por Elaborador"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.firma == "":
        tarea = current_user.launch_task(
            nombre="cid_procedimientos.tasks.crear_pdf",
            descripcion=f"Crear archivo PDF de {cid_procedimiento.titulo_procedimiento}",
            usuario_id=current_user.id,
            cid_procedimiento_id=cid_procedimiento.id,
            accept_reject_url=url_for("cid_procedimientos.accept_reject", cid_procedimiento_id=cid_procedimiento.id),
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    else:
        flash("Este procedimiento ya ha sido firmado.", "warning")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))


@cid_procedimientos.route("/cid_procedimientos/aceptar_rechazar/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def accept_reject(cid_procedimiento_id):
    """Aceptar o Rechazar un Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not cid_procedimiento.seguimiento in ["ELABORADO", "REVISADO"]:
        flash("Este procedimiento no puede ser aceptado o rechazado.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    form = CIDProcedimientoAcceptRejectForm()
    if form.validate_on_submit():
        # Si fue aceptado
        if form.aceptar.data is True:
            # Crear un nuevo registro
            nuevo = CIDProcedimiento(
                titulo_procedimiento=cid_procedimiento.titulo_procedimiento,
                codigo=cid_procedimiento.codigo,
                revision=cid_procedimiento.revision,
                fecha=cid_procedimiento.fecha,
                objetivo=cid_procedimiento.objetivo,
                alcance=cid_procedimiento.alcance,
                documentos=cid_procedimiento.documentos,
                definiciones=cid_procedimiento.definiciones,
                responsabilidades=cid_procedimiento.responsabilidades,
                desarrollo=cid_procedimiento.desarrollo,
                registros=cid_procedimiento.registros,
                elaboro_nombre=cid_procedimiento.elaboro_nombre,
                elaboro_puesto=cid_procedimiento.elaboro_puesto,
                elaboro_email=cid_procedimiento.elaboro_email,
                reviso_nombre=cid_procedimiento.reviso_nombre,
                reviso_puesto=cid_procedimiento.reviso_puesto,
                reviso_email=cid_procedimiento.reviso_email,
                aprobo_nombre=cid_procedimiento.aprobo_nombre,
                aprobo_puesto=cid_procedimiento.aprobo_puesto,
                aprobo_email=cid_procedimiento.aprobo_email,
                control_cambios=cid_procedimiento.control_cambios,
            )
            nuevo.cadena = cid_procedimiento.cadena + 1
            # Si este procedimiento fue elaborado, sigue revisarlo
            if cid_procedimiento.seguimiento == "ELABORADO":
                nuevo.seguimiento = "EN REVISION"
                nuevo.seguimiento_posterior = "EN REVISION"
                usuario = Usuario.query.filter_by(email=cid_procedimiento.reviso_email).first()
                if usuario:
                    nuevo.usuario = usuario
                else:
                    flash(f"No fue encontrado el usuario con e-mail {cid_procedimiento.reviso_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
            # Si este procedimiento fue revisado, sigue autorizarlo
            if cid_procedimiento.seguimiento == "REVISADO":
                nuevo.seguimiento = "EN AUTORIZACION"
                nuevo.seguimiento_posterior = "EN AUTORIZACION"
                usuario = Usuario.query.filter_by(email=cid_procedimiento.aprobo_email).first()
                if usuario:
                    nuevo.usuario = usuario
                else:
                    flash(f"No fue encontrado el usuario con e-mail {cid_procedimiento.aprobo_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
            nuevo.anterior_id = cid_procedimiento.id
            nuevo.firma = ""
            nuevo.archivo = ""
            nuevo.url = ""
            nuevo.save()
            # TODO: Falta cambiar seguimiento_posterior en anterior_id
            flash("Usted ha aceptado revisar/autorizar este procedimiento.", "success")
            return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=nuevo.id))
        # Fue rechazado
        if form.rechazar.data is True:
            # Preguntar porque fue rechazado
            flash("Usted ha rechazado revisar/autorizar este procedimiento.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    form.titulo_procedimiento.data = cid_procedimiento.titulo_procedimiento
    form.codigo.data = cid_procedimiento.codigo
    form.revision.data = cid_procedimiento.revision
    form.seguimiento.data = cid_procedimiento.seguimiento
    form.seguimiento_posterior.data = cid_procedimiento.seguimiento_posterior
    return render_template("cid_procedimientos/accept_reject.jinja2", form=form, cid_procedimiento=cid_procedimiento)


@cid_procedimientos.route("/cid_procedimientos/eliminar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(cid_procedimiento_id):
    """Eliminar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "A":
        cid_procedimiento.seguimiento = "CANCELADO POR ELABORADOR"
        cid_procedimiento.delete()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} eliminado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


@cid_procedimientos.route("/cid_procedimientos/recuperar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(cid_procedimiento_id):
    """Recuperar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "B":
        cid_procedimiento.seguimiento = "EN ELABORACION"
        cid_procedimiento.recover()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} recuperado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))
