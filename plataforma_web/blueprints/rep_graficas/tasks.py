"""
Rep Graficas, tareas en el fondo
"""
from datetime import datetime
import logging

from plataforma_web.app import create_app
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.blueprints.bitacoras.models import Bitacora

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("rep_graficas.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def elaborar(rep_grafica_id: int):
    """Elaborar gráfica"""
    bitacora.info("Inicia")
    cantidad = 0

    # Terminar tarea
    mensaje = f"Termina con {cantidad} resultados."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
