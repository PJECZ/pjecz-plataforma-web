"""
Listas de Acuerdos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

listas_de_acuerdos = Blueprint('listas_de_acuerdos', __name__, template_folder='templates')


@listas_de_archivos.before_request
@login_required
@permission_required(Permiso.OBSERVADOR)
def before_request():
    pass


