"""
Rep Graficas, tareas en el fondo

- elaborar: Elaborar los reportes pendientes de una gráfica
"""
from datetime import datetime, timedelta
import logging
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.rep_graficas.models import RepGrafica
from plataforma_web.blueprints.rep_reportes.models import RepReporte


bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("rep_graficas.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def elaborar(rep_grafica_id: int):
    """Elaborar los reportes pendientes de una gráfica"""

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

    # Si no tiene reportes
    if len(rep_grafica.rep_reportes) == 0:
        if rep_grafica.corte == 'DIARIO':
            puntero = rep_grafica.desde
            cantidad = 0
            while puntero <= rep_grafica.hasta:
                inicio = datetime(year=puntero.year, month=puntero.month, day=puntero.day, hour=0, minute=0, second=0)
                termino = datetime(year=puntero.year, month=puntero.month, day=puntero.day, hour=23, minute=59, second=59)
                siguiente_dia = (termino + timedelta(days=1)).date()
                programado = datetime(year=siguiente_dia.year, month=siguiente_dia.month, day=siguiente_dia.day, hour=0, minute=0, second=0)
                RepReporte(
                    rep_grafica=rep_grafica,
                    descripcion="Reporte diario del " + puntero.strftime("%Y-%m-%d"),
                    inicio=inicio,
                    termino=termino,
                    programado=programado,
                    progreso="PENDIENTE",
                ).save()
                puntero += timedelta(days=1)
                cantidad += 1
            mensaje = f"Para {rep_grafica.descripcion} se crearon {cantidad} reportes."
            bitacora.info(mensaje)
        else:
            mensaje = set_task_error("La gráfica no tiene reportes.")
            bitacora.error(mensaje)
            return mensaje

    # Elaborar reportes pendientes
    hoy = datetime.now()
    cantidad = 0
    for rep_reporte in rep_grafica.rep_reportes:
        if rep_reporte.estatus == "A" and rep_reporte.progreso == "PENDIENTE" and rep_reporte.programado <= hoy:
            app.task_queue.enqueue(
                "plataforma_web.blueprints.rep_reportes.tasks.elaborar",
                rep_reporte_id=rep_reporte.id,
            )
            cantidad += 1

    # Terminar tarea
    if cantidad > 0:
        mensaje = f"Para {rep_grafica.descripcion} se lanzaron {cantidad} reportes por elaborar."
    else:
        mensaje = f"Para {rep_grafica.descripcion} no se elaboraron reportes."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
