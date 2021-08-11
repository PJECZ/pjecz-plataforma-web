"""
Sistemas, vistas
"""
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

sistemas = Blueprint("sistemas", __name__, template_folder="templates")


@sistemas.route("/")
def start():
    """Página inicial"""
    if current_user.is_authenticated:
        versiones = url_for("static", filename="json/versiones.json")
        return render_template("sistemas/start.jinja2", versiones=versiones)
    return redirect("/login")


@sistemas.app_errorhandler(400)
def bad_request(error):
    """Solicitud errónea"""
    return render_template("sistemas/403.jinja2", error=error), 403


@sistemas.app_errorhandler(403)
def forbidden(error):
    """Acceso no autorizado"""
    return render_template("sistemas/403.jinja2"), 403


@sistemas.app_errorhandler(404)
def page_not_found(error):
    """Error página no encontrada"""
    return render_template("sistemas/404.jinja2"), 404


@sistemas.app_errorhandler(500)
def internal_server_error(error):
    """Error del servidor"""
    return render_template("sistemas/500.jinja2"), 500
