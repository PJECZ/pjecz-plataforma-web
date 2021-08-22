"""
CID Registros, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_registros.forms import CIDRegistroForm
from plataforma_web.blueprints.cid_registros.models import CIDRegistro

cid_registros = Blueprint("cid_registros", __name__, template_folder="templates")

MODULO = "DOCUMENTACIONES"


@cid_registros.before_request
@login_required
@permission_required(Permiso.VER_DOCUMENTACIONES)
def before_request():
    """ Permiso por defecto """


@cid_registros.route("/cid_registros")
def list_active():
    """ Listado de CID Registros activos """
    cid_registros_activos = CIDRegistro.query.filter_by(estatus="A").order_by(CIDRegistro.creado.desc()).limit(100).all()
    return render_template("cid_registros/list.jinja2", cid_registros=cid_registros_activos, estatus="A")


@cid_registros.route("/cid_registros/inactivos")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def list_inactive():
    """ Listado de CID Registros inactivos """
    cid_registros_inactivos = CIDRegistro.query.filter_by(estatus="B").order_by(CIDRegistro.creado.desc()).limit(100).all()
    return render_template("cid_registros/list.jinja2", cid_registros=cid_registros_inactivos, estatus="B")


@cid_registros.route("/cid_registros/<int:cid_registro_id>")
def detail(cid_registro_id):
    """ Detalle de un CID Registro """
    cid_registro = CIDRegistro.query.get_or_404(cid_registro_id)
    return render_template("cid_registros/detail.jinja2", cid_registro=cid_registro)


@cid_registros.route("/cid_registros/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_DOCUMENTACIONES)
def new():
    """ Nuevo CID Registro """
    form = CIDRegistroForm()
    if form.validate_on_submit():
        cid_registro = CIDRegistro(
            descripcion=form.descripcion.data,
            formato=form.formato.data,
        )
        cid_registro.save()
        flash(f"CID Registro {cid_registro.descripcion} guardado.", "success")
        return redirect(url_for("cid_registros.detail", cid_registro_id=cid_registro.id))
    return render_template("cid_registros/new.jinja2", form=form)


@cid_registros.route("/cid_registros/edicion/<int:cid_registro_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def edit(cid_registro_id):
    """ Editar CID Registro """
    cid_registro = CIDRegistro.query.get_or_404(cid_registro_id)
    form = CIDRegistroForm()
    if form.validate_on_submit():
        cid_registro.descripcion = form.descripcion.data
        cid_registro.formato = form.formato.data
        cid_registro.save()
        flash(f"CID Registro {cid_registro.descripcion} guardado.", "success")
        return redirect(url_for("cid_registros.detail", cid_registro_id=cid_registro.id))
    form.descripcion.data = cid_registro.descripcion
    form.formato.data = cid_registro.formato
    return render_template("cid_registros/edit.jinja2", form=form, cid_registro=cid_registro)


@cid_registros.route("/cid_registros/eliminar/<int:cid_registro_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def delete(cid_registro_id):
    """ Eliminar CID Registro """
    cid_registro = CIDRegistro.query.get_or_404(cid_registro_id)
    if cid_registro.estatus == "A":
        cid_registro.delete()
        flash(f"CID Registro {cid_registro.descripcion} eliminado.", "success")
    return redirect(url_for("cid_registros.detail", cid_registro_id=cid_registro_id))


@cid_registros.route("/cid_registros/recuperar/<int:cid_registro_id>")
@permission_required(Permiso.MODIFICAR_DOCUMENTACIONES)
def recover(cid_registro_id):
    """ Recuperar CID Registro """
    cid_registro = CIDRegistro.query.get_or_404(cid_registro_id)
    if cid_registro.estatus == "B":
        cid_registro.recover()
        flash(f"CID Registro {cid_registro.descripcion} recuperado.", "success")
    return redirect(url_for("cid_registros.detail", cid_registro_id=cid_registro_id))
