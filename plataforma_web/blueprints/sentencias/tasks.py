"""
Sentencias, tareas para ejecutar en el fondo
"""

import base64
import csv
from datetime import datetime, date
import locale
import logging
import os
from pathlib import Path
import random
import re

from dateutil.tz import tzlocal
from dotenv import load_dotenv
from google.cloud import storage
import sendgrid
from sendgrid.helpers.mail import Attachment, ContentId, Disposition, Email, FileContent, FileName, FileType, To, Content, Mail

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/sentencias.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_MX.utf8")


def enviar_reporte():
    """Enviar via correo electronico el reporte de sentencias"""

    # Fecha
    fecha = date.today()

    # Iniciar tarea
    mensaje_inicial = f"Inicia enviar reporte de sentencias del {fecha}"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

    # Momento en que se elabora este reporte
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")
    subject = f"Sentencias del {fecha.strftime('%d/%B/%Y')}"

    # Definir la ruta al archivo temporal CSV
    random_hex = "%030x" % random.randrange(16**30)
    reporte_ruta = Path("/tmp/reporte-sentencias-" + random_hex + ".csv")
    reporte_archivo = f"reporte-sentencias-{fecha.strftime('%Y-%m-%d')}.csv"

    # Cabecera
    bitacora.info("Inicia enviar reporte de %s", momento_str)
    contenidos = [f"<h1>PJECZ Plataforma Web</h1><h2>{subject}</h2><p>Fecha de elaboración: {momento_str}.<br>ESTE MENSAJE ES ELABORADO POR UN PROGRAMA. FAVOR DE NO RESPONDER.</p>"]

    # Contenido
    sentencias = Sentencia.query.order_by(Sentencia.id.desc()).limit(50).all()
    if len(sentencias) == 0:
        bitacora.warning("No hay sentencias")
    else:
        contador = 0
        with open(reporte_ruta, "w", encoding="utf8") as puntero:
            reporte = csv.writer(puntero)
            reporte.writerow(
                [
                    "ID",
                    "Autoridades",
                    "Fechas",
                    "Sentencias",
                    "Expedientes",
                    "Materias",
                    "Tipos de Juicios",
                    "URLs",
                ]
            )
            for sentencia in sentencias:
                reporte.writerow(
                    [
                        sentencia.id,
                        sentencia.autoridad.clave,
                        sentencia.fecha,
                        sentencia.sentencia,
                        sentencia.expediente,
                        sentencia.materia_tipo_juicio.materia.nombre,
                        sentencia.materia_tipo_juicio.descripcion,
                        sentencia.url,
                    ]
                )
                contador += 1
        bitacora.info("Se han escrito %d sentencias en el archivo CSV.", contador)

    # Si no hay contenido, no enviar nada
    if contador == 0:
        mensaje = "No se va enviar nada porque no hay sentencias."
        bitacora.info(mensaje)
    else:
        # Preparar el mensaje para manadr con SendGrid
        api_key = os.getenv("SENDGRID_API_KEY", "")
        if api_key == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_API_KEY"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=api_key)
        from_str = os.getenv("SENDGRID_FROM_EMAIL", "")
        if from_str == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_FROM_EMAIL"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        from_email = Email(from_str)
        to_str = os.getenv("SENDGRID_TO_EMAIL_REPORTES", "")
        if to_str == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_TO_EMAIL_REPORTES"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        to_email = To(to_str)
        content = Content("text/html", "<br>".join(contenidos))
        mail = Mail(from_email, to_email, subject, content)
        # Adjuntar el archivo CSV
        with open(reporte_ruta, "r", encoding="utf8") as puntero:
            datos = puntero.read()
            puntero.close()
        encoded = base64.b64encode(bytes(datos, "utf8")).decode("utf8")
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType("text/csv")
        attachment.file_name = FileName(reporte_archivo)
        attachment.disposition = Disposition("attachment")
        attachment.content_id = ContentId("ArchivoCSV")
        mail.attachment = attachment
        # Enviar el mensaje
        sendgrid_client.client.mail.send.post(request_body=mail.get())
        # Eliminar el archivo CSV
        reporte_ruta.unlink(missing_ok=True)

    # Terminar tarea
    mensaje_final = f"Termina enviar reporte de sentencias del {fecha}"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final
