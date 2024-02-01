"""
Usuarios Solicitudes, tareas en el fondo
"""
from datetime import datetime
import locale
import logging
import os

import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Email, To, Content, Mail

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("usuarios_solicitudes.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
db.app = app

load_dotenv()  # Take environment variables from .env

EXPIRACION_HORAS = 48
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "")
VALIDACION_EMAIL_PERSONAL_URL = os.getenv("VALIDACION_EMAIL_PERSONAL_URL", "")
MAX_NUM_INTENTOS = 3


def enviar_email_validacion(usuario_solicitud_id: int):
    """Enviar usuario solicitud para validación de email"""

    # Consultar
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    # Validar el número de intentos
    if usuario_solicitud.intentos_email >= MAX_NUM_INTENTOS:
        # Terminar tarea
        set_task_progress(100)
        mensaje_final = f"No se ha enviado el mensaje al correo {usuario_solicitud.email_personal} por exceso de intentos."
        bitacora.info(mensaje_final)
        return mensaje_final

    # Bandera para saber si se tienen todos los elementos necesarios
    bandera = True

    # Momento en que se elabora este mensaje
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")

    # URL
    url = None
    if VALIDACION_EMAIL_PERSONAL_URL != "":
        url = f"{VALIDACION_EMAIL_PERSONAL_URL}/{usuario_solicitud.id}"
    else:
        bitacora.warning("Falta declarar la variable: VALIDACION_EMAIL_PERSONAL_URL.")
        bandera = False

    # Contenidos
    contenidos = [
        "<h1>Plataforma Web</h1>",
        "<h2>PODER JUDICIAL DEL ESTADO DE COAHUILA DE ZARAGOZA</h2>",
        f"<p>Fecha de elaboración: {momento_str}.</p>",
        "<p>Ingrese el token recibido en el enlace de más abajo para validar que usted es el dueño de este correo electrónico.</p>",
        "<h2>TOKEN</h2>",
        f"<h1><code>{usuario_solicitud.token_email}</code></h1>",
        f"<a href='{url}'>enlace de validación</a>",
    ]
    content = Content("text/html", "".join(contenidos))

    # Remitente
    from_email = None
    if SENDGRID_FROM_EMAIL != "":
        from_email = Email(SENDGRID_FROM_EMAIL)
    else:
        bitacora.warning("Falta declarar la variable: SENDGRID_FROM_EMAIL.")
        bandera = False

    # Destinatario
    to_email = To(usuario_solicitud.email_personal)

    # Asunto
    subject = "Validación de email personal para el sistema - Plataforma Web"

    # SendGrid
    sendgrid_client = None
    if SENDGRID_API_KEY != "":
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    else:
        bitacora.warning("Falta declarar la variable: SENDGRID_API_KEY.")
        bandera = False

    # Enviar mensaje
    mensaje_final = ""
    if bandera:
        mail = Mail(from_email, to_email, subject, content)
        sendgrid_client.client.mail.send.post(request_body=mail.get())
        usuario_solicitud.intentos_email = usuario_solicitud.intentos_email + 1
        usuario_solicitud.save()
        mensaje_final = f"Se ha enviado el mensaje número {usuario_solicitud.intentos_email} al correo {usuario_solicitud.email_personal}"
        bitacora.info(mensaje_final)
    else:
        mensaje_final = f"Se omite el envió a {usuario_solicitud.email_personal} por que faltan elementos"
        bitacora.warning(mensaje_final)

    # Terminar tarea
    set_task_progress(100)
    return mensaje_final
