"""
CID Registros, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.cid_registros.models import CIDRegistro

cid_registros = Blueprint("cid_registros", __name__, template_folder="templates")


@cid_registros.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """ Permiso por defecto """


@cid_registros.route("/cid_registros")
def list_active():
    """ Listado de CID Registros activos """
    cid_registros_activos = CIDRegistro.query.filter(CIDRegistro.estatus == "A").order_by(CIDRegistro.creado.desc()).limit(100).all()
    return render_template("cid_registros/list.jinja2", cid_registros=cid_registros_activos, estatus="A")
