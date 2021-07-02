"""
CID Formatos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_formatos.forms import CIDFormatoForm
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

cid_formatos = Blueprint("cid_formatos", __name__, template_folder="templates")


@cid_formatos.before_request
@login_required
@permission_required(Permiso.VER_DOCUMENTACIONES)
def before_request():
    """ Permiso por defecto """


@cid_formatos.route("/cid_formatos")
def list_active():
    """ Listado de CID Formatos activos """
    cid_formatos_activos = CIDFormato.query.filter(CIDFormato.estatus == "A").order_by(CIDFormato.creado.desc()).limit(100).all()
    return render_template("cid_formatos/list.jinja2", cid_formatos=cid_formatos_activos, estatus="A")


@cid_formatos.route("/cid_formatos/inactivos")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def list_inactive():
    """ Listado de CID Formatos inactivos """
    cid_formatos_inactivos = CIDFormato.query.filter(CIDFormato.estatus == "B").order_by(CIDFormato.creado.desc()).limit(100).all()
    return render_template("cid_formatos/list.jinja2", cid_formatos=cid_formatos_inactivos, estatus="B")


@cid_formatos.route("/cid_formatos/<int:cid_formato_id>")
def detail(cid_formato_id):
    """ Detalle de un CID Formato """
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    return render_template("cid_formatos/detail.jinja2", cid_formato=cid_formato)


@cid_formatos.route("/cid_formatos/nuevo/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_DOCUMENTACIONES)
def new(cid_procedimiento_id):
    """ Nuevo CID Formato """

    # Validar procedimiento
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus != "A":
        flash("El procedmiento no es activo.", "warning")
        return redirect(url_for("cid_procedimientos.list_active"))

    # Si viene el formulario
    form = CIDFormatoForm()
    if form.validate_on_submit():
        cid_formato = CIDFormato(
            procedimiento=cid_procedimiento,
            descripcion=form.descripcion.data,
        )
        cid_formato.save()
        flash(f"CID Formato {cid_formato.descripcion} guardado.", "success")
        return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato.id))

    # Mostrar formulario
    form.procedim
    return render_template("cid_formatos/new.jinja2", form=form)


@cid_formatos.route("/cid_formatos/edicion/<int:cid_formato_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def edit(cid_formato_id):
    """ Editar CID Formato """
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    form = CIDFormatoForm()
    if form.validate_on_submit():
        cid_formato.descripcion = form.descripcion.data
        cid_formato.save()
        flash(f"CID Formato {cid_formato.descripcion} guardado.", "success")
        return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato.id))
    form.descripcion.data = cid_formato.descripcion
    form.procedimiento.data = cid_formato.procedimiento
    return render_template("cid_formatos/edit.jinja2", form=form, cid_formato=cid_formato)


@cid_formatos.route("/cid_formatos/eliminar/<int:cid_formato_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def delete(cid_formato_id):
    """ Eliminar CID Formato """
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    if cid_formato.estatus == "A":
        cid_formato.delete()
        flash(f"CID Formato {cid_formato.descripcion} eliminado.", "success")
    return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato_id))


@cid_formatos.route("/cid_formatos/recuperar/<int:cid_formato_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def recover(cid_formato_id):
    """ Recuperar CID Formato """
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    if cid_formato.estatus == "B":
        cid_formato.recover()
        flash(f"CID Formato {cid_formato.descripcion} recuperado.", "success")
    return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato_id))
