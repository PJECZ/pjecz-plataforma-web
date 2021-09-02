"""
CID Procedimientos, vistas
"""
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_procedimientos.forms import CIDProcedimientoForm
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.cid_formatos.models import CIDFormato

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")

MODULO = "DOCUMENTACIONES"


@cid_procedimientos.before_request
@login_required
@permission_required(Permiso.VER_DOCUMENTACIONES)
def before_request():
    """Permiso por defecto"""


@cid_procedimientos.route("/cid_procedimientos")
def list_active():
    """Listado de CID Procedimientos activos"""
    cid_procedimientos_activos = CIDProcedimiento.query.filter_by(estatus="A").order_by(CIDProcedimiento.id).limit(100).all()
    return render_template("cid_procedimientos/list.jinja2", cid_procedimientos=cid_procedimientos_activos, estatus="A")


@cid_procedimientos.route("/cid_procedimientos/inactivos")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def list_inactive():
    """Listado de CID Procedimientos inactivos"""
    cid_procedimientos_inactivos = CIDProcedimiento.query.filter_by(estatus="B").order_by(CIDProcedimiento.id).limit(100).all()
    return render_template("cid_procedimientos/list.jinja2", cid_procedimientos=cid_procedimientos_inactivos, estatus="B")


@cid_procedimientos.route("/cid_procedimientos/<int:cid_procedimiento_id>")
def detail(cid_procedimiento_id):
    """Detalle de un CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    cid_formatos = CIDFormato.query.filter(CIDFormato.procedimiento == cid_procedimiento).filter(CIDFormato.estatus == "A").order_by(CIDFormato.id).all()
    return render_template("cid_procedimientos/detail.jinja2", cid_procedimiento=cid_procedimiento, cid_formatos=cid_formatos)


@cid_procedimientos.route("/cid_procedimientos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_DOCUMENTACIONES)
def new():
    """Nuevo CID Procedimiento"""
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        cid_procedimiento = CIDProcedimiento(
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
            elaboro_nombre=form.elaboro_nombre.data,
            elaboro_puesto=form.elaboro_puesto.data,
            elaboro_email=form.elaboro_email.data,
            reviso_nombre=form.reviso_nombre.data,
            reviso_puesto=form.reviso_puesto.data,
            reviso_email=form.reviso_email.data,
            aprobo_nombre=form.aprobo_nombre.data,
            aprobo_puesto=form.aprobo_puesto.data,
            aprobo_email=form.aprobo_email.data,
            control_cambios=form.control_cambios.data,
        )
        cid_procedimiento.save()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    return render_template("cid_procedimientos/new.jinja2", form=form)


@cid_procedimientos.route("/cid_procedimientos/edicion/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def edit(cid_procedimiento_id):
    """Editar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        cid_procedimiento.titulo_procedimiento=form.titulo_procedimiento.data
        cid_procedimiento.codigo=form.codigo.data
        cid_procedimiento.revision=form.revision.data
        cid_procedimiento.fecha=form.fecha.data
        cid_procedimiento.objetivo=form.objetivo.data
        cid_procedimiento.alcance=form.alcance.data
        cid_procedimiento.documentos=form.documentos.data
        cid_procedimiento.definiciones=form.definiciones.data
        cid_procedimiento.responsabilidades=form.responsabilidades.data
        cid_procedimiento.desarrollo=form.desarrollo.data
        cid_procedimiento.registros=form.registros.data
        cid_procedimiento.elaboro_nombre=form.elaboro_nombre.data
        cid_procedimiento.elaboro_puesto=form.elaboro_puesto.data
        cid_procedimiento.elaboro_email=form.elaboro_email.data
        cid_procedimiento.reviso_nombre=form.reviso_nombre.data
        cid_procedimiento.reviso_puesto=form.reviso_puesto.data
        cid_procedimiento.reviso_email=form.reviso_email.data
        cid_procedimiento.aprobo_nombre=form.aprobo_nombre.data
        cid_procedimiento.aprobo_puesto=form.aprobo_puesto.data
        cid_procedimiento.aprobo_email=form.aprobo_email.data
        cid_procedimiento.control_cambios=form.control_cambios.data
        cid_procedimiento.save()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    form.titulo_procedimiento.data=cid_procedimiento.titulo_procedimiento
    form.codigo.data=cid_procedimiento.codigo
    form.revision.data=cid_procedimiento.revision
    form.fecha.data=cid_procedimiento.fecha
    form.objetivo.data=cid_procedimiento.objetivo
    form.alcance.data=cid_procedimiento.alcance
    form.documentos.data=cid_procedimiento.documentos
    form.definiciones.data=cid_procedimiento.definiciones
    form.responsabilidades.data=cid_procedimiento.responsabilidades
    form.desarrollo.data=cid_procedimiento.desarrollo
    form.registros.data=cid_procedimiento.registros
    form.elaboro_nombre.data=cid_procedimiento.elaboro_nombre
    form.elaboro_puesto.data=cid_procedimiento.elaboro_puesto
    form.elaboro_email.data=cid_procedimiento.elaboro_email
    form.reviso_nombre.data=cid_procedimiento.reviso_nombre
    form.reviso_puesto.data=cid_procedimiento.reviso_puesto
    form.reviso_email.data=cid_procedimiento.reviso_email
    form.aprobo_nombre.data=cid_procedimiento.aprobo_nombre
    form.aprobo_puesto.data=cid_procedimiento.aprobo_puesto
    form.aprobo_email.data=cid_procedimiento.aprobo_email
    form.control_cambios.data=cid_procedimiento.control_cambios
    return render_template("cid_procedimientos/edit.jinja2", form=form, cid_procedimiento=cid_procedimiento)


@cid_procedimientos.route("/cid_procedimientos/eliminar/<int:cid_procedimiento_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def delete(cid_procedimiento_id):
    """Eliminar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "A":
        cid_procedimiento.delete()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} eliminado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


@cid_procedimientos.route("/cid_procedimientos/recuperar/<int:cid_procedimiento_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def recover(cid_procedimiento_id):
    """Recuperar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "B":
        cid_procedimiento.recover()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} recuperado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))
