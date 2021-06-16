"""
CID Procedimientos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_procedimientos.forms import CIDProcedimientoForm
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")


@cid_procedimientos.before_request
@login_required
@permission_required(Permiso.VER_DOCUMENTACIONES)
def before_request():
    """ Permiso por defecto """


@cid_procedimientos.route("/cid_procedimientos")
def list_active():
    """ Listado de CID Procedimientos activos """
    cid_procedimientos_activos = CIDProcedimiento.query.filter(CIDProcedimiento.estatus == "A").order_by(CIDProcedimiento.creado.desc()).limit(100).all()
    return render_template("cid_procedimientos/list.jinja2", cid_procedimientos=cid_procedimientos_activos, estatus="A")


@cid_procedimientos.route("/cid_procedimientos/inactivos")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def list_inactive():
    """ Listado de CID Procedimientos inactivos """
    cid_procedimientos_inactivos = CIDProcedimiento.query.filter(CIDProcedimiento.estatus == "B").order_by(CIDProcedimiento.creado.desc()).limit(100).all()
    return render_template("cid_procedimientos/list.jinja2", cid_procedimientos=cid_procedimientos_inactivos, estatus="B")


@cid_procedimientos.route("/cid_procedimientos/<int:cid_procedimiento_id>")
def detail(cid_procedimiento_id):
    """ Detalle de un CID Procedimiento """
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    return render_template("cid_procedimientos/detail.jinja2", cid_procedimiento=cid_procedimiento)


@cid_procedimientos.route("/cid_procedimientos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_DOCUMENTACIONES)
def new():
    """ Nuevo CID Procedimiento """
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        cid_procedimiento = CIDProcedimiento(descripcion=form.descripcion.data)
        cid_procedimiento.save()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    return render_template("cid_procedimientos/new.jinja2", form=form)


@cid_procedimientos.route("/cid_procedimientos/edicion/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def edit(cid_procedimiento_id):
    """ Editar CID Procedimiento """
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        cid_procedimiento.descripcion = form.descripcion.data
        cid_procedimiento.save()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} guardado.", "success")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
    form.descripcion.data = cid_procedimiento.descripcion
    return render_template("cid_procedimientos/edit.jinja2", form=form, cid_procedimiento=cid_procedimiento)


@cid_procedimientos.route("/cid_procedimientos/eliminar/<int:cid_procedimiento_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def delete(cid_procedimiento_id):
    """ Eliminar CID Procedimiento """
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "A":
        cid_procedimiento.delete()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} eliminado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


@cid_procedimientos.route("/cid_procedimientos/recuperar/<int:cid_procedimiento_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def recover(cid_procedimiento_id):
    """ Recuperar CID Procedimiento """
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus == "B":
        cid_procedimiento.recover()
        flash(f"CID Procedimiento {cid_procedimiento.descripcion} recuperado.", "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))
