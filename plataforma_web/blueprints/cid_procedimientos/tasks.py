"""
CID Procedimientos, tareas en el fondo

- crear_pdf: Crear PDF
- exportar_xlsx: Exportar Procedimientos a un archivo XLSX
"""

import json
import locale
import logging
import os
from pathlib import Path
import random
from typing import Tuple

from delta import html
from jinja2 import Environment, FileSystemLoader
import pdfkit
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

from lib.storage import GoogleCloudStorage, NoneFilenameError, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.cid_formatos.models import CIDFormato

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/cid_procedimientos.log")
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

    # Iniciar tarea
    mensaje_inicial = f"Inicia crear PDF de {cid_procedimiento.titulo_procedimiento}"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

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
    # Ciclo de conversion de JSON para colocar tabla en PDF Registros
    tabla_registros = json.dumps(cid_procedimiento.registros)
    renglones_json = json.loads(tabla_registros)
    tabla_renglon = ""
    for renglon in renglones_json:
        tabla_renglon += "<tr>"
        for i in renglones_json[renglon]:
            tabla_renglon += "<td align='center' style='border-bottom:1px solid #C5C5C5'>" + i + "</td>"
        tabla_renglon += "</tr>"

    # Ciclo de conversion de JSON para colocar tabla en PDF Control de Cambios
    tabla_cambios = json.dumps(cid_procedimiento.control_cambios)
    renglones_cambio_json = json.loads(tabla_cambios)
    tabla_cambio_renglon = ""
    for renglon in renglones_cambio_json:
        tabla_cambio_renglon += "<tr>"
        for i in renglones_cambio_json[renglon]:
            tabla_cambio_renglon += "<td align='center' style='border-bottom:1px solid #C5C5C5'>" + i + "</td>"
        tabla_cambio_renglon += "</tr>"

    # Renderizar Body
    pdf_body_plantilla = entorno.get_template("pdf_body.html")
    pdf_body_html = pdf_body_plantilla.render(
        objetivo=html.render(cid_procedimiento.objetivo["ops"]),
        alcance=html.render(cid_procedimiento.alcance["ops"]),
        documentos=html.render(cid_procedimiento.documentos["ops"]),
        definiciones=html.render(cid_procedimiento.definiciones["ops"]),
        responsabilidades=html.render(cid_procedimiento.responsabilidades["ops"]),
        desarrollo=html.render(cid_procedimiento.desarrollo["ops"]),
        registros=tabla_renglon,
        control_cambios=tabla_cambio_renglon,
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
    random_hex = "%030x" % random.randrange(16**30)
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

    # Crear archivo PDF y subirlo a Google Cloud Storage
    archivo_pdf = None
    try:
        archivo_pdf = pdfkit.from_string(pdf_body_html, False, options=wkhtmltopdf_options)
    except IOError as error:
        mensaje = set_task_error("No fue posible crear el archivo PDF.")
        bitacora.warning(mensaje, str(error))
    if archivo_pdf is not None:
        storage = GoogleCloudStorage(DEPOSITO_DIR, allowed_extensions=["pdf"])
        try:
            storage.set_filename(
                hashed_id=cid_procedimiento.encode_id(),
                description=cid_procedimiento.titulo_procedimiento,
                extension="pdf",
            )
            storage.upload(archivo_pdf)
            cid_procedimiento.archivo = storage.filename
            cid_procedimiento.url = storage.url
            cid_procedimiento.save()
            bitacora.info("Se ha subido %s a Google Cloud Storage.", cid_procedimiento.archivo)
        except NotConfiguredError:
            mensaje = set_task_error("No fue posible subir el archivo PDF a Google Storage porque falta la configuración.")
            bitacora.warning(mensaje)
        except (NotAllowedExtesionError, UnknownExtesionError, NoneFilenameError) as error:
            mensaje = set_task_error("No fue posible subir el archivo PDF a Google Storage por un error de tipo de archivo.")
            bitacora.warning(mensaje, str(error))
        except Exception as error:
            mensaje = set_task_error("No fue posible subir el archivo PDF a Google Storage.")
            bitacora.warning(mensaje, str(error))

    # Eliminar archivos temporales
    path_header.unlink(missing_ok=True)
    path_footer.unlink(missing_ok=True)

    # Elaborar firma
    cid_procedimiento.firma = cid_procedimiento.elaborar_firma()
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
        mensaje = set_task_error("No se pudo definir la cadena de seguimiento.")
        bitacora.warning(mensaje)

    # Guardar registro en la base de datos
    cid_procedimiento.save()

    # Preparar SendGrid
    send_grid = None
    from_email = None
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    email_sendgrid = os.environ.get("EMAIL_SENDGRID", "plataforma.web@pjecz.gob.mx")
    if api_key != "":
        send_grid = sendgrid.SendGridAPIClient(api_key=api_key)
    if email_sendgrid != "":
        from_email = Email(email_sendgrid)

    # Si seguimiento es ELABORADO
    if send_grid and cid_procedimiento.seguimiento == "ELABORADO":
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
        send_grid.client.mail.send.post(request_body=mail.get())
        bitacora.info("Se enviado un mensaje a %s para que revise.", cid_procedimiento.reviso_email)

    # Si seguimiento es REVISADO
    if send_grid and cid_procedimiento.seguimiento == "REVISADO":
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
        send_grid.client.mail.send.post(request_body=mail.get())
        bitacora.info("Se enviado un mensaje a %s para que autorice.", cid_procedimiento.aprobo_email)
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
        send_grid.client.mail.send.post(request_body=mail.get())
        bitacora.info("Se enviado un mensaje a %s para informar.", cid_procedimiento.elaboro_email)

    # Si seguimiento es AUTORIZADO
    if send_grid and cid_procedimiento.seguimiento == "AUTORIZADO":
        # Notificar al elaborador y al revisor que fue autorizado
        anterior = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        while anterior:
            anterior.seguimiento_posterior = "AUTORIZADO"
            anterior.save()
            anterior = CIDProcedimiento.query.get(anterior.anterior_id)
        # TODO: Enviar mensaje para informar al elaborador
        # TODO: Enviar mensaje para informar al revisor

    # Terminar tarea
    mensaje_final = f"Termina crear PDF de {cid_procedimiento.titulo_procedimiento}"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final


def exportar_xlsx() -> Tuple[str, str, str]:
    """Exportar Procedimientos a un archivo XLSX"""
    bitacora.info("Inicia exportar Usuarios Datos a un archivo XLSX")

    # Pruebas
    contador = 23
    nombre_archivo_xlsx = "cid_procedimientos.xlsx"
    public_url = "https://storage.googleapis.com/pjecz-plataforma-web/cid_procedimientos/cid_procedimientos.xlsx"

    # Entregar mensaje de termino, el nombre del archivo XLSX y la URL publica
    mensaje_termino = f"Se exportaron {contador} Usuarios-Datos a {nombre_archivo_xlsx}"
    bitacora.info(mensaje_termino)
    return mensaje_termino, nombre_archivo_xlsx, public_url
