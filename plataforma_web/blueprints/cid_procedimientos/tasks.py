"""
CID Procedimientos, tareas en el fondo

- crear_pdf: Crear PDF
"""
import locale
import logging
import os
from pathlib import Path
import random

from delta import html
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader
import pdfkit
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("cid_procedimientos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

DEPOSITO_DIR = "cid_procedimientos"
TEMPLATES_DIR = "plataforma_web/blueprints/cid_procedimientos/templates/cid_procedimientos"


def crear_pdf(cid_procedimiento_id: int, usuario_id: int = None, accept_reject_url: str = ""):
    """Crear PDF"""

    # Validar procedimiento
    cid_procedimiento = CIDProcedimiento.query.get(cid_procedimiento_id)
    if cid_procedimiento is None:
        mensaje = set_task_error(f"El procedimiento con id {cid_procedimiento_id} no exite.")
        bitacora.error(mensaje)
        return mensaje
    if cid_procedimiento.estatus != "A":
        mensaje = set_task_error(f"El procedimiento con id {cid_procedimiento_id} no es activo.")
        bitacora.error(mensaje)
        return mensaje
    if cid_procedimiento.archivo != "" or cid_procedimiento.url != "":
        mensaje = set_task_error(f"El procedimiento con id {cid_procedimiento_id} ya tiene un archivo PDF.")
        bitacora.error(mensaje)
        return mensaje
    if not cid_procedimiento.seguimiento in ["EN ELABORACION", "EN REVISION", "EN AUTORIZACION"]:
        mensaje = set_task_error(f"El procedimiento con id {cid_procedimiento_id} tiene un seguimiento incorrecto.")
        bitacora.error(mensaje)
        return mensaje

    # Poner en bitácora información de arranque
    bitacora.info("Crear PDF de %s", cid_procedimiento.titulo_procedimiento)
    bitacora.info("Directorio actual: %s", os.getcwd())

    # Juntar las firmas
    elaboro_firma = ""
    reviso_firma = ""
    autorizo_firma = ""
    if cid_procedimiento.seguimiento == "EN ELABORACION":
        # Firmas: elaboró
        elaboro_firma = cid_procedimiento.elaborar_firma()
    elif cid_procedimiento.seguimiento == "EN REVISION":
        # Firmas: elaboró y revisó
        procedimiento_elaboro = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        elaboro_firma = procedimiento_elaboro.firma
        reviso_firma = cid_procedimiento.elaborar_firma()
    elif cid_procedimiento.seguimiento == "EN AUTORIZACION":
        # Firmas: autorizó, elaboró y revisó
        procedimiento_reviso = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        reviso_firma = procedimiento_reviso.firma
        procedimiento_elaboro = CIDProcedimiento.query.get(procedimiento_reviso.anterior_id)
        elaboro_firma = procedimiento_elaboro.firma
        autorizo_firma = cid_procedimiento.elaborar_firma()

    # Renderizar HTML con el apoyo de
    # - Jinja2 https://palletsprojects.com/p/jinja/
    # - Quill Delta https://pypi.org/project/quill-delta/
    entorno = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Renderizar Header
    pdf_header_plantilla = entorno.get_template("pdf_header.html")
    pdf_header_html = pdf_header_plantilla.render(
        titulo_procedimiento=cid_procedimiento.titulo_procedimiento,
        codigo=cid_procedimiento.codigo,
        revision=str(cid_procedimiento.revision),
        fecha=cid_procedimiento.fecha.strftime("%d %b %Y"),
    )
    # Renderizar Footer
    pdf_footer_plantilla = entorno.get_template("pdf_footer.html")
    pdf_footer_html = pdf_footer_plantilla.render(
        codigo=cid_procedimiento.codigo,
        revision=str(cid_procedimiento.revision),
        fecha=cid_procedimiento.fecha.strftime("%d %b %Y"),
    )
    # Renderizar Body
    pdf_body_plantilla = entorno.get_template("pdf_body.html")
    pdf_body_html = pdf_body_plantilla.render(
        objetivo=html.render(cid_procedimiento.objetivo["ops"]),
        alcance=html.render(cid_procedimiento.alcance["ops"]),
        documentos=html.render(cid_procedimiento.documentos["ops"]),
        definiciones=html.render(cid_procedimiento.definiciones["ops"]),
        responsabilidades=html.render(cid_procedimiento.responsabilidades["ops"]),
        desarrollo=html.render(cid_procedimiento.desarrollo["ops"]),
        registros=html.render(cid_procedimiento.registros["ops"]),
        control_cambios=html.render(cid_procedimiento.control_cambios["ops"]),
        elaboro_nombre=cid_procedimiento.elaboro_nombre,
        elaboro_puesto=cid_procedimiento.elaboro_puesto,
        reviso_nombre=cid_procedimiento.reviso_nombre,
        reviso_puesto=cid_procedimiento.reviso_puesto,
        aprobo_nombre=cid_procedimiento.aprobo_nombre,
        aprobo_puesto=cid_procedimiento.aprobo_puesto,
        elaboro_firma=elaboro_firma,
        reviso_firma=reviso_firma,
        autorizo_firma=autorizo_firma,
    )

    # Definir las rutas de los archivos temporales
    random_hex = "%030x" % random.randrange(16 ** 30)
    path_header = Path("/tmp/pjecz_plataforma_web-" + random_hex + "-header.html")
    path_footer = Path("/tmp/pjecz_plataforma_web-" + random_hex + "-footer.html")

    # Guardar archivo temporal con el header
    archivo = open(path_header, "w", encoding="utf8")
    archivo.write(pdf_header_html)
    archivo.close()

    # Guardar archivo temporal con el footer
    archivo = open(path_footer, "w", encoding="utf8")
    archivo.write(pdf_footer_html)
    archivo.close()

    # Opciones de configuracion para Header y Footer
    wkhtmltopdf_options = {
        "enable-local-file-access": False,
        "javascript-delay": 2000,
        "header-html": path_header,
        "footer-html": path_footer,
    }

    # Crear archivo PDF con el apoyo de
    # - https://pypi.org/project/pdfkit/
    # - https://wkhtmltopdf.org/downloads.html
    pdf = None
    try:
        pdf = pdfkit.from_string(pdf_body_html, False, options=wkhtmltopdf_options)
    except IOError as error:
        mensaje = str(error)
        bitacora.error(mensaje)
        # return mensaje

    # Subir a Google Storage
    archivo = ""
    url = ""
    cloud_stotage_deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO", "")
    if pdf is not None and cloud_stotage_deposito != "":
        archivo = cid_procedimiento.archivo_pdf()
        storage_client = storage.Client()
        bucket = storage_client.bucket(cloud_stotage_deposito)
        blob = bucket.blob(DEPOSITO_DIR + "/" + archivo)
        blob.upload_from_string(pdf, content_type="application/pdf")
        url = blob.public_url

    # Eliminar archivos temporales
    path_header.unlink(missing_ok=True)
    path_footer.unlink(missing_ok=True)

    # Actualizar registro
    cid_procedimiento.firma = cid_procedimiento.elaborar_firma()
    cid_procedimiento.archivo = archivo
    cid_procedimiento.url = url

    if cid_procedimiento.seguimiento == "EN ELABORACION":
        # Primer firma en la cadena
        cid_procedimiento.cadena = 1
        cid_procedimiento.seguimiento = "ELABORADO"
        cid_procedimiento.seguimiento_posterior = "ELABORADO"
    elif cid_procedimiento.seguimiento == "EN REVISION":
        # Segunda firma en la cadena
        cid_procedimiento.cadena = 2
        cid_procedimiento.seguimiento = "REVISADO"
        cid_procedimiento.seguimiento_posterior = "REVISADO"
    elif cid_procedimiento.seguimiento == "EN AUTORIZACION":
        # Segunda firma en la cadena
        cid_procedimiento.cadena = 3
        cid_procedimiento.seguimiento = "AUTORIZADO"
        cid_procedimiento.seguimiento_posterior = "AUTORIZADO"
    else:
        # Algo anda mal
        mensaje = set_task_error("El seguimiento no es lo que se esperaba.")
        bitacora.error(mensaje)
        return mensaje

    # Guardar cambios en archivo, url, firma, cadena, seguimiento y seguimiento_posterior
    cid_procedimiento.save()

    # Preparar SendGrid
    sg = None
    from_email = None
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    email_sendgrid = os.environ.get("EMAIL_SENDGRID", "plataforma.web@pjecz.gob.mx")
    if api_key != "":
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
    if email_sendgrid != "":
        from_email = Email(email_sendgrid)

    # Si seguimiento es ELABORADO
    if sg and cid_procedimiento.seguimiento == "ELABORADO":
        # Enviar mensaje para aceptar o rechazar al revisor
        subject = "Solicitud para aceptar o rechazar la revisión de un procedimiento"
        mensaje_plantilla = entorno.get_template("message_accept_reject.html")
        mensaje_html = mensaje_plantilla.render(
            subject=subject,
            destinatario_nombre=cid_procedimiento.reviso_nombre,
            cid_procedimiento=cid_procedimiento,
            accept_reject_url=accept_reject_url,
            remitente_nombre=cid_procedimiento.elaboro_nombre,
            host=os.environ.get("HOST", ""),
        )
        to_email = To(cid_procedimiento.reviso_email)
        content = Content("text/html", mensaje_html)
        mail = Mail(from_email, to_email, subject, content)
        sg.client.mail.send.post(request_body=mail.get())

    # Si seguimiento es REVISADO
    if sg and cid_procedimiento.seguimiento == "REVISADO":
        # Notificar al elaborador que fue revisado
        anterior = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        while anterior:
            anterior.seguimiento_posterior = "REVISADO"
            anterior.save()
            anterior = CIDProcedimiento.query.get(anterior.anterior_id)
        # Enviar mensaje para aceptar o rechazar al autorizador
        subject = "Solicitud para aceptar o rechazar la autorización de un procedimiento"
        mensaje_plantilla = entorno.get_template("message_accept_reject.html")
        mensaje_html = mensaje_plantilla.render(
            subject=subject,
            destinatario_nombre=cid_procedimiento.aprobo_nombre,
            cid_procedimiento=cid_procedimiento,
            accept_reject_url=accept_reject_url,
            remitente_nombre=cid_procedimiento.reviso_nombre,
            host=os.environ.get("HOST", ""),
        )
        to_email = To(cid_procedimiento.aprobo_email)
        content = Content("text/html", mensaje_html)
        mail = Mail(from_email, to_email, subject, content)
        sg.client.mail.send.post(request_body=mail.get())
        # Enviar mensaje para informar al elaborador
        subject = "Ya fue revisado el procedimiento"
        mensaje_plantilla = entorno.get_template("message_signed.html")
        mensaje_html = mensaje_plantilla.render(
            subject=subject,
            destinatario_nombre=cid_procedimiento.elaboro_nombre,
            cid_procedimiento=cid_procedimiento,
        )
        to_email = To(cid_procedimiento.elaboro_email)
        content = Content("text/html", mensaje_html)
        mail = Mail(from_email, to_email, subject, content)
        sg.client.mail.send.post(request_body=mail.get())

    # Si seguimiento es AUTORIZADO
    if sg and cid_procedimiento.seguimiento == "AUTORIZADO":
        # Notificar al elaborador y al revisor que fue autorizado
        anterior = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        while anterior:
            anterior.seguimiento_posterior = "AUTORIZADO"
            anterior.save()
            anterior = CIDProcedimiento.query.get(anterior.anterior_id)
        # TODO: Enviar mensaje para informar al elaborador
        # TODO: Enviar mensaje para informar al revisor

    # Terminar tarea
    mensaje = "Listo " + url
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
