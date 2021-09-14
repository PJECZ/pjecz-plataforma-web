"""
CID Procedimientos, tareas en el fondo

- crear_pdf: Crear PDF
"""
import locale
import logging
import os

from delta import html
from jinja2 import Environment, FileSystemLoader

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

TEMPLATES_DIR = "plataforma_web/blueprints/cid_procedimientos/templates/cid_procedimientos"


def crear_pdf(cid_procedimiento_id: int):
    """Crear PDF"""

    # Validar procedimiento
    cid_procedimiento = CIDProcedimiento.query.get(cid_procedimiento_id)
    if cid_procedimiento is None:
        mensaje = set_task_error("El procedimiento no exite.")
        bitacora.error(mensaje)
        return mensaje
    if cid_procedimiento.estatus != "A":
        mensaje = set_task_error("El procedimiento no es activo.")
        bitacora.error(mensaje)
        return mensaje

    # Poner en bitácora información de arranque
    bitacora.info("Directorio actual: %s", os.getcwd())
    bitacora.info("Título: %s", cid_procedimiento.titulo_procedimiento)

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

    # Monstrar en terminal el resultado
    print(pdf_body_html)

    # Crear archivo PDF con el apoyo de
    # - pdfkit https://pypi.org/project/pdfkit/

    # Mensaje de término
    mensaje = "Terminado"
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
