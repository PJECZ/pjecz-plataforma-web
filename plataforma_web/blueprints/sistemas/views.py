"""
Sistemas, vistas
"""
from datetime import date, datetime, timedelta

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from plataforma_web.blueprints.sentencias.models import Sentencia

sistemas = Blueprint("sistemas", __name__, template_folder="templates")

HOY = date.today()
BREVE_LIMITE_DIAS = 15
BREVE_DESDE_DATETIME = datetime(year=HOY.year, month=HOY.month, day=HOY.day) + timedelta(days=-BREVE_LIMITE_DIAS)

TARJETA_SATISFACTORIA = "bg-light"
TARJETA_ADVERTENCIA = "bg-warning"
TARJETA_VACIA = "bg-danger"
TARJETAS_LIMITE_REGISTROS = 5


@sistemas.route("/inicio/audiencias_json")
def audiencias_json():
    """Audiencias en JSON"""
    if current_user.autoridad.audiencia_categoria == "NO DEFINIDO":
        return {}


@sistemas.route("/inicio/edictos_json")
def edictos_json():
    """Edictos en JSON"""
    if current_user.autoridad.directorio_edictos == "":
        return {}


@sistemas.route("/inicio/listas_de_acuerdos_json")
def listas_de_acuerdos_json():
    """Listas de Acuerdos en JSON"""
    if current_user.autoridad.directorio_listas_de_acuerdos != "":
        return {}


@sistemas.route("/inicio/sentencias_json")
def sentencias_json():
    """Sentencias en JSON"""
    if current_user.autoridad.directorio_sentencias != "":
        return {}
    sentencias = Sentencia.query.filter(Sentencia.autoridad == current_user.autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for sentencia in sentencias.order_by(Sentencia.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "sentencia": sentencia.sentencia,
                "materia_tipo_juicio": sentencia.materia_tipo_juicio.descripcion,
                "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = sentencias.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = sentencias.filter(Sentencia.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca a subido V.P. de Sentencias."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "V.P. de Sentencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("sentencias.list_active"),
        "style": estilo,
    }


@sistemas.route("/")
def start():
    """Página inicial"""
    if current_user.is_authenticated:
        return render_template("sistemas/start.jinja2")
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
