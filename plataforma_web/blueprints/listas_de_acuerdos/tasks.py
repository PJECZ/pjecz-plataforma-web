"""
Listas de Acuerdos, tareas para ejecutar en el fondo
"""
import logging
from datetime import datetime
from pathlib import Path

import google.cloud.storage
from rq import get_current_job

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.tareas.models import Tarea

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
empunadura = logging.FileHandler("listas_de_acuerdos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

DEPOSITO = "pjecz-consultas"
SUBDIRECTORIO = "Listas de Acuerdos"


def set_task_progress(progress: int):
    """ Cambiar el progreso de la tarea """
    bitacora.info("- Progreso %d %%", progress)
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea and progress >= 100:
            tarea.ha_terminado = True
            tarea.save()


def construir():
    """ Construir la estructura de directorios y archivos para Pelican """


def rastrear(usuario_id, autoridad_id):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    bitacora.info("Inicia listas_de_acuerdos.tasks.rastrear")
    # Consultar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is False:
        return  # No es válida la autoridad
    if autoridad.listas_de_acuerdos == "":
        return  # No tiene listas de acuerdos
    bitacora.info("- Distrito %s", autoridad.distrito.nombre)
    bitacora.info("- Autoridad %s", autoridad.descripcion)
    # Consultar listas de acuerdos
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad_id == autoridad_id).all()
    fechas = [lista_de_acuerdo.fecha for lista_de_acuerdo in listas_de_acuerdos]
    bitacora.info("- En la base de datos hay %d listas de acuerdos", len(fechas))
    # Rastrear en Google Cloud Storage
    bucket = google.cloud.storage.Client().get_bucket(DEPOSITO)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total = len(blobs)
    if total == 0:
        return  # No exite el subdirectorio o no tiene archivos
    bitacora.info("- En Storage hay %d listas de acuerdos", total)
    # Arrancar tarea
    set_task_progress(0)
    contador = 0
    contador_agregados = 0
    bloque = int(len(blobs) / 20)  # 20 veces se va a actualizar el avance
    bloque_siguiente = bloque
    for blob in blobs:
        # Cambiar el avance de la tarea
        contador += 1
        if contador >= bloque_siguiente:
            set_task_progress(round(100 * contador / len(blobs)))
            bloque_siguiente += bloque
        # Validar
        ruta = Path(blob.name)
        archivo = ruta.name
        fecha_str = archivo[:10]
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            continue  # No es válida la fecha
        if ruta.suffix.lower() != ".pdf":
            continue  # No es un PDF
        if len(archivo) > 14:  # YYYY-MM-DD.pdf
            descripcion = archivo[11:-4].strip()
        else:
            descripcion = ""
        # Revisar si ya existe en la BD
        if fecha in fechas:
            continue  # Ya existe en la BD
        # Insertar
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            archivo=archivo,
            fecha=fecha,
            descripcion=descripcion,
            url=blob.public_url,
        )
        lista_de_acuerdo.save()
        contador_agregados += 1
    # Terminar tarea
    set_task_progress(100)
    bitacora.info("- Se agregaron %d listas de acuerdos", contador_agregados)
    bitacora.info("Termina listas_de_acuerdos.tasks.rastrear")
    return f"Se agregaron {contador_agregados} listas de acuerdos"


def respaldar():
    """ Respaldar la base de datos para descargar como archivo CSV """
