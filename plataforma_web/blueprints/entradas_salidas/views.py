"""
Entradas-Salidas, vistas
"""
from flask import Blueprint, render_template
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida

entradas_salidas = Blueprint("entradas_salidas", __name__, template_folder="templates")


@entradas_salidas.route("/entradas_salidas")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def list_active():
    """ Listado de entradas y salidas """
    entradas_salidas_activas = EntradaSalida.query.limit(400).all()
    return render_template("entradas_salidas/list.jinja2", entradas_salidas=entradas_salidas_activas)
