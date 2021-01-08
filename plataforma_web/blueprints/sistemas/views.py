"""
Sistemas, vistas
"""
from datetime import datetime
from flask import Blueprint, redirect, render_template
from flask_login import current_user

sistemas = Blueprint('sistemas', __name__, template_folder='templates')


@sistemas.route('/')
def start():
    """ Página inicial """
    if current_user.is_authenticated:
        return render_template('sistemas/start.html')
    return redirect('/login')


@sistemas.app_errorhandler(403)
def forbidden(error):
    """ Acceso no autorizado """
    return render_template('sistemas/403.html'), 403


@sistemas.app_errorhandler(404)
def page_not_found(error):
    """ Error página no encontrada """
    return render_template('sistemas/404.html'), 404


@sistemas.app_errorhandler(500)
def internal_server_error(error):
    """ Error del servidor """
    return render_template('sistemas/500.html'), 500
