"""
Rep Graficas, tareas en el fondo
"""
import logging
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.rep_graficas.models import RepGrafica


bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("rep_graficas.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def elaborar(rep_grafica_id: int):
    """Elaborar reportes pendientes de una gráfica"""
    bitacora.info("Inicia")
    cantidad = 0

    # Validar gráfica
    rep_grafica = RepGrafica.query.get(rep_grafica_id)
    if rep_grafica is None:
        mensaje = set_task_error("La gráfica no exite.")
        bitacora.error(mensaje)
        return mensaje
    if rep_grafica.estatus != "A":
        mensaje = set_task_error("La gráfica no es activa.")
        bitacora.error(mensaje)
        return mensaje
    if len(rep_grafica.rep_reportes) == 0:
        mensaje = set_task_error("Esta gráfica no tiene reportes.")
        bitacora.warning(mensaje)
        return mensaje

    # Elaborar reportes pendientes
    for rep_reporte in rep_grafica.rep_reportes:
        if rep_reporte.estatus == 'A' and rep_reporte.progreso == 'PENDIENTE':
            app.task_queue.enqueue(
                "plataforma_web.blueprints.rep_reportes.tasks.elaborar",
                rep_reporte_id=rep_reporte.id,
            )
            cantidad += 1

    # Terminar tarea
    mensaje = f"Se lanzaron {cantidad} reportes por elaborar."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
