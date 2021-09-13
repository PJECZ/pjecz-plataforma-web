"""
CID Procedimientos, tareas en el fondo
"""
import logging

from jinja2 import Environment, FileSystemLoader
import os
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

TEMPLATES_DIR = "plataforma_web/blueprints/cid_procedimientos/templates/cid_procedimientos"


def crear_pdf(cid_procedimiento_id: int):
    """Crear PDF"""

    cid_procedimiento = CIDProcedimiento.query.get(cid_procedimiento_id)
    if cid_procedimiento is None:
        mensaje = set_task_error("El procedimiento no exite.")
        bitacora.error(mensaje)
        return mensaje
    if cid_procedimiento.estatus != "A":
        mensaje = set_task_error("El procedimiento no es activo.")
        bitacora.error(mensaje)
        return mensaje

    bitacora.info("Directorio: %s", os.getcwd())
    bitacora.info("Título: %s", cid_procedimiento.titulo_procedimiento)
    bitacora.info("Codigo: %s, Revision: %d", cid_procedimiento.codigo, cid_procedimiento.revision)

    entorno = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    body_plantilla = entorno.get_template("pdf_body.html")
    body_html = body_plantilla.render(
        titulo_procedimiento=cid_procedimiento.titulo_procedimiento,
        codigo=cid_procedimiento.codigo,
        revision=str(cid_procedimiento.revision),
        objetivo=cid_procedimiento.objetivo,
    )
    print(body_html)

    mensaje = "Terminado"
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
