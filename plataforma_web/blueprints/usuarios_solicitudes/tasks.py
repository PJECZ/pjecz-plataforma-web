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
from twilio.rest import Client

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
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_TEL_FROM = os.getenv("TWILIO_TEL_FROM", "")
VALIDACION_TELEFONO_PERSONAL_URL = os.getenv("VALIDACION_TELEFONO_PERSONAL_URL", "")


def enviar_email_validacion(usuario_solicitud_id: int):
    """Enviar mensaje para validar el email personal del usuario"""

    # Validar que se tiene VALIDACION_EMAIL_PERSONAL_URL
    if VALIDACION_EMAIL_PERSONAL_URL == "":
        mensaje_error = "ERROR: No esta configurada la variable VALIDACION_EMAIL_PERSONAL_URL."
        bitacora.error(mensaje_error)
        return mensaje_error

    # Validar que se tiene el remitente
    if SENDGRID_FROM_EMAIL == "":
        mensaje_error = "ERROR: No esta configurada la variable SENDGRID_FROM_EMAIL."
        bitacora.error(mensaje_error)
        return mensaje_error
    from_email = Email(SENDGRID_FROM_EMAIL)

    # Validar que se tiene SENDGRID_API_KEY y crear el cliente de SendGrid
    if SENDGRID_API_KEY == "":
        mensaje_error = "ERROR: No esta configurada la variable SENDGRID_API_KEY."
        bitacora.error(mensaje_error)
        return mensaje_error
    sendgrid_client = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    # Iniciar tarea
    mensaje_inicial = f"Iniciando enviar mensaje para validar el email personal del usuario ID: {usuario_solicitud_id}"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

    # Consultar la solicitud
    usuario_solicitud = UsuarioSolicitud.query.get(usuario_solicitud_id)

    # Si la consulta no arroja resultados, casua error y se termina
    if usuario_solicitud is None:
        mensaje_error = "ERROR: No se encontró la solicitud."
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Si la solicitud esta eliminada, causa error y se termina
    if usuario_solicitud.estatus != "A":
        mensaje_error = f"ERROR: La solicitud {usuario_solicitud_id} esta eliminada."
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Definir el URL que ira en el mensaje para validar el email personal
    url = f"{VALIDACION_EMAIL_PERSONAL_URL}{usuario_solicitud.encode_id()}"

    # Si intentos_email es mayor o igual a MAX_NUM_INTENTOS, se termina la tarea
    if usuario_solicitud.intentos_email >= MAX_NUM_INTENTOS:
        mensaje_error = f"No se envió el mensaje a {usuario_solicitud.email_personal} porque llegó al máximo de intentos."
        set_task_error(mensaje_error)
        bitacora.warning(mensaje_error)
        return mensaje_error

    # Momento en que se elabora este mensaje
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")

    # Elaborar el contenido del mensaje de correo electronico
    contenidos = [
        "<h1>Plataforma Web</h1>",
        "<h2>PODER JUDICIAL DEL ESTADO DE COAHUILA DE ZARAGOZA</h2>",
        f"<p>Fecha de elaboración: {momento_str}.</p>",
        "<p>Ingrese el token recibido en el enlace de más abajo para validar que usted es el dueño de este correo electrónico.</p>",
        "<h2>TOKEN</h2>",
        f"<h1><code>{usuario_solicitud.token_email}</code></h1>",
        f"<h3><a href='{url}'>enlace de validación</a></h3>",
    ]
    content = Content("text/html", "".join(contenidos))

    # Definir el destinatario
    to_email = To(usuario_solicitud.email_personal)

    # Definir el asunto
    subject = "Validación de email personal para el sistema - Plataforma Web"

    # Enviar mensaje
    try:
        mail = Mail(from_email, to_email, subject, content)
        sendgrid_client.client.mail.send.post(request_body=mail.get())
    except Exception as e:
        mensaje_error = f"ERROR: No se envió el mensaje a {usuario_solicitud.email_personal} por error de SendGrid. {e}"
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Terminar tarea
    mensaje_final = f"Termina enviar mensaje para validar el email personal {usuario_solicitud.email_personal} del usuario"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final


def enviar_sms_validacion(usuario_solicitud_id: int) -> str:
    """Enviar SMS vía Twilio al celular del usuario"""

    # Validar que se tiene VALIDACION_TELEFONO_PERSONAL_URL
    if VALIDACION_TELEFONO_PERSONAL_URL == "":
        mensaje_error = "ERROR: NO esta configurada la variable VALIDACION_TELEFONO_PERSONAL_URL."
        bitacora.error(mensaje_error)
        return mensaje_error

    # Validar que se tiene TWILIO_ACCOUNT_SID
    if TWILIO_ACCOUNT_SID == "":
        mensaje_error = "ERROR: NO esta configurada la variable TWILIO_ACCOUNT_SID."
        bitacora.error(mensaje_error)
        return mensaje_error

    # Validar que se tiene TWILIO_AUTH_TOKEN
    if TWILIO_AUTH_TOKEN == "":
        mensaje_error = "ERROR: NO esta configurada la variable TWILIO_AUTH_TOKEN."
        bitacora.error(mensaje_error)
        return mensaje_error

    # Validar que se tiene TWILIO_TEL_FROM
    if TWILIO_TEL_FROM == "":
        mensaje_error = "ERROR: NO esta configurada la variable TWILIO_TEL_FROM."
        bitacora.error(mensaje_error)
        return mensaje_error

    # Iniciar tarea
    mensaje_inicial = f"Iniciando enviar SMS vía Twilio al celular del usuario ID: {usuario_solicitud_id}"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

    # Consultar la solicitud
    usuario_solicitud = UsuarioSolicitud.query.get(usuario_solicitud_id)

    # Si la consulta no arroja resultados, casua error y se termina
    if usuario_solicitud is None:
        mensaje_error = "ERROR: No se encontró la solicitud."
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Si la solicitud esta eliminada, causa error y se termina
    if usuario_solicitud.estatus != "A":
        mensaje_error = f"ERROR: La solicitud {usuario_solicitud_id} esta eliminada."
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Si no se encuentra la solicitud, causa error y se termina
    if usuario_solicitud is None:
        mensaje_error = "ERROR: No se encontró la solicitud o esta eliminada."
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Definir el URL que ira en el mensaje
    url = f"{VALIDACION_TELEFONO_PERSONAL_URL}{usuario_solicitud.encode_id()}"

    # Si intentos_email es mayor o igual a MAX_NUM_INTENTOS, se termina la tarea
    if usuario_solicitud.intentos_telefono_celular >= MAX_NUM_INTENTOS:
        mensaje_error = f"AVISO: No se envió el SMS a {usuario_solicitud.telefono_celular} porque llegó al máximo de intentos."
        set_task_error(mensaje_error)
        bitacora.warning(mensaje_error)
        return mensaje_error

    # Creamos el SMS de twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Enviar mensaje
    try:
        client.messages.create(
            body=f"Ingrese este token {usuario_solicitud.token_telefono_celular} en {url}",
            from_=TWILIO_TEL_FROM,
            to=f"+52{usuario_solicitud.telefono_celular}",
        )
    except Exception as e:
        mensaje_error = f"ERROR: No se envió el sms a {usuario_solicitud.telefono_celular} por error de Twilio. {e}"
        set_task_error(mensaje_error)
        bitacora.error(mensaje_error)
        return mensaje_error

    # Terminar tarea
    mensaje_final = f"Termina enviar SMS vía Twilio al celular del usuario {usuario_solicitud.telefono_celular}"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final
