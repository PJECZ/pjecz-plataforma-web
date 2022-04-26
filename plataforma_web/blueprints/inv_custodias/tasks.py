"""
Inventario Custodia, tareas en el fondo

- crear_pdf: Crear PDF
"""
import locale
import logging
from pathlib import Path
import random

from jinja2 import Environment, FileSystemLoader

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.inv_custodias.models import InvCustodia

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("inv_custodias.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_Mx.utf8")

DEPOSITO_DIR = "inv_custodias"
TEMPLATES_DIR = "plataforma_web/blueprints/inv_custodias/templates/inv_custodias"


def crear_pdf(inv_custodia_id: int, usuario_id: int = None, accept_reject_url: str = ""):
    """Crear PDF"""

    # Validar Custodia
    inv_custodia = InvCustodia.query.get(inv_custodia_id)
    if inv_custodia is None:
        mensaje = set_task_error(f"La custodia con id {inv_custodia_id} no existe.")
        bitacora.error(mensaje)
        return mensaje
    if inv_custodia.estatus != "A":
        mensaje = set_task_error(f"La custodia con id {inv_custodia_id} no esta activa.")
        bitacora.error(mensaje)
        return mensaje
    if inv_custodia.archivo != "" or inv_custodia.url != "":
        mensaje = set_task_error(f"La custodia con id {inv_custodia_id} ya tiene un archivo PDF.")
        bitacora.error(mensaje)
        return mensaje

    # Poner en bitácora información de arranque
    bitacora.info("Crear PDF de %s", inv_custodia.nombre_completo)
    # bitacora.info("Directorio actual: %s", os.getcwd())

    # Renderizar HTML con el apoyo fr
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
        nombre_completo=inv_custodia.nombre_completo,
        curp=inv_custodia.usuario.curp,
        oficina=inv_custodia.usuario.oficina.clave_nombre,
        puesto=inv_custodia.usuario.puesto,
        fecha=inv_custodia.fecha.strtime("%d %b %y"),
    )

    # Definir las rutas de los archivos temporales
    random_hex = "%030x" % random.randrange(16**30)
    path_header = Path("/tmp/pjecz_plataforma_web-" + random_hex + "-header.html")

    # Guardar archivo temporal con el header
    archivo = open(path_header, "w", encoding="utf8")
    archivo.write(pdf_header_html)
    archivo.close()

    # Opciones de configuracion para Header y Footer
    wkhtmltopdf_options = {
        "enable-local-file-access": False,
        "javascript-delay": 2000,
        "header-html": path_header,
    }

    # # Crear archivo PDF y subirlo a Google Cloud Storage
    # archivo_pdf = None
    # try:
    #     archivo_pdf = pdfkit.from_string()

    # Eliminar archivos temporales
    path_header.unlink(missing_ok=True)

    # Guardar registro en la base de datos
    inv_custodia.save()

    # Terminar tarea
    mensaje = "Tarea finalizada"
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
