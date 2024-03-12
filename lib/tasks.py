"""
Tasks
"""

from rq import get_current_job
from plataforma_web.blueprints.tareas.models import Tarea


def set_task_progress(progreso: int, mensaje: str = "", archivo: str = "", url: str = "") -> None:
    """Cambiar el progreso de la tarea"""
    job = get_current_job()
    if job:
        job.meta["progress"] = progreso
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            hay_cambios = False
            if archivo != "" and archivo != tarea.archivo:
                tarea.archivo = archivo
                hay_cambios = True
            if url != "" and url != tarea.url:
                tarea.url = url
                hay_cambios = True
            if progreso < 100 and tarea.ha_terminado is True:
                tarea.ha_terminado = False
                hay_cambios = True
            if progreso >= 100 and tarea.ha_terminado is False:
                tarea.ha_terminado = True
                hay_cambios = True
            if mensaje != tarea.mensaje:
                tarea.mensaje = mensaje
                hay_cambios = True
            if hay_cambios:
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
            tarea.mensaje = mensaje
            tarea.save()
    return mensaje
