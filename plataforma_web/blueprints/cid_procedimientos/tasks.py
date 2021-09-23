"""
CID Procedimientos, tareas en el fondo

- crear_pdf: Crear PDF
"""
import locale
import logging
import os

from delta import html
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader
import pdfkit

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

locale.setlocale(locale.LC_TIME, "es_MX")

DEPOSITO_DIR = "cid_procedimientos"
TEMPLATES_DIR = "plataforma_web/blueprints/cid_procedimientos/templates/cid_procedimientos"


def crear_pdf(cid_procedimiento_id: int, usuario_id: int = None):
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

    # Renderizar HTML con el apoyo de
    # - Jinja2 https://palletsprojects.com/p/jinja/
    # - Quill Delta https://pypi.org/project/quill-delta/
    entorno = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    pdf_body_plantilla = entorno.get_template("pdf_body.html")
    pdf_body_html = pdf_body_plantilla.render(
        titulo_procedimiento=cid_procedimiento.titulo_procedimiento,
        codigo=cid_procedimiento.codigo,
        revision=str(cid_procedimiento.revision),
        fecha=cid_procedimiento.fecha.strftime("%d %b %Y"),
        objetivo=html.render(cid_procedimiento.objetivo["ops"]),
        alcance=html.render(cid_procedimiento.alcance["ops"]),
        documentos=html.render(cid_procedimiento.documentos["ops"]),
        definiciones=html.render(cid_procedimiento.definiciones["ops"]),
        responsabilidades=html.render(cid_procedimiento.responsabilidades["ops"]),
        desarrollo=html.render(cid_procedimiento.desarrollo["ops"]),
        registros=html.render(cid_procedimiento.registros["ops"]),
    )

    # Crear archivo PDF con el apoyo de
    # - pdfkit https://pypi.org/project/pdfkit/
    try:
        pdf = pdfkit.from_string(pdf_body_html, False)
    except IOError as error:
        mensaje = str(error)
        bitacora.error(mensaje)
        return mensaje

    # Subir a Google Storage
    archivo = cid_procedimiento.archivo_pdf()
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ.get("CLOUD_STORAGE_DEPOSITO"))
    blob = bucket.blob(DEPOSITO_DIR + "/" + archivo)
    blob.upload_from_string(pdf, content_type="application/pdf")
    url = blob.public_url

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

    # Guardar cambios
    cid_procedimiento.save()

    # Notificar al elaborador que fue revisado
    if cid_procedimiento.seguimiento == "REVISADO":
        anterior = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        while anterior is not None:
            anterior.seguimiento_posterior = "REVISADO"
            anterior.save()
            anterior = CIDProcedimiento.query.get(anterior.anterior_id)

    # Notificar al elaborador y al revisor que fue autorizado
    if cid_procedimiento.seguimiento == "AUTORIZADO":
        anterior = CIDProcedimiento.query.get(cid_procedimiento.anterior_id)
        while anterior is not None:
            anterior.seguimiento_posterior = "AUTORIZADO"
            anterior.save()
            anterior = CIDProcedimiento.query.get(anterior.anterior_id)

    # Terminar tarea
    mensaje = "Listo " + url
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
