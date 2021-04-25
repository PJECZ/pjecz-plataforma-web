"""
CID Formatos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.cid_formatos.models import CIDFormato

cid_formatos = Blueprint("cid_formatos", __name__, template_folder="templates")


@cid_formatos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """ Permiso por defecto """


@cid_formatos.route("/cid_formatos")
def list_active():
    """ Listado de CID Formatos activos """
    cid_formatos_activos = CIDFormato.query.filter(CIDFormato.estatus == "A").order_by(CIDFormato.creado.desc()).limit(100).all()
    return render_template("cid_formatos/list.jinja2", cid_formatos=cid_formatos_activos, estatus="A")


@cid_formatos.route("/cid_formatos/inactivos")
def list_inactive():
    """ Listado de CID Formatos inactivos """
    cid_formatos_inactivos = CIDFormato.query.filter(CIDFormato.estatus == "B").order_by(CIDFormato.creado.desc()).limit(100).all()
    return render_template("cid_formatos/list.jinja2", cid_formatos=cid_formatos_inactivos, estatus="B")


@cid_formatos.route("/cid_formatos/<int:cid_formato_id>")
def detail(cid_formato_id):
    """ Detalle de un CID Formato """
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    return render_template("cid_formatos/detail.jinja2", cid_formato=cid_formato)
