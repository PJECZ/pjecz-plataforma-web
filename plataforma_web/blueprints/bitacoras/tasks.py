"""
Bitacoras, tareas para ejecutar en el fondo
"""
import logging
import os
from rq import get_current_job
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To

from plataforma_web.app import create_app
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.tareas.models import Tarea

tronco = logging.getLogger(__name__)
tronco.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("bitacoras.log")
empunadura.setFormatter(formato)
tronco.addHandler(empunadura)

app = create_app()
app.app_context().push()


def set_task_progress(progress: int, mensaje: str = None):
    """Cambiar el progreso de la tarea"""
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            if progress >= 100:
                tarea.ha_terminado = True
            if mensaje is not None:
                tarea.descripcion = mensaje
            tarea.save()


def set_task_error(mensaje: str):
    """Al fallar la tarea debe tomar el mensaje y terminarla"""
    job = get_current_job()
    if job:
        job.meta["progress"] = 100
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            tarea.ha_terminado = True
            tarea.descripcion = mensaje
            tarea.save()
    tronco.error(mensaje)
    tronco.info("Termina")
    return mensaje


def enviar(usuario_id: int = None):
    """Enviar reporte"""

    # Iniciar la tarea y contadores
    set_task_progress(0)

    # Sendgrid
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY", "BAD-API-KEY"))
    from_email = Email("test@example.com")
    to_email = To("test@example.com")
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    # Mensaje final
    mensaje_final = "He terminado."

    # Terminar tarea
    set_task_progress(100)
    tronco.info(mensaje_final)
    return mensaje_final
