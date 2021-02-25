"""
Tasks, tareas para ejecutar en el fondo

    rq worker plataforma-web-tasks

    from redis import Redis
    import rq
    queue = rq.Queue('plataforma-web-tasks', connection=Redis.from_url('redis://'))
    job = queue.enqueue('plataforma_web.blueprints.listas_de_acuerdos.tasks.example', 25)
    job.refresh()
    job.meta
    Out[21]: {'progress': 16.0}

"""
from datetime import datetime
from pathlib import Path
import time

from google.cloud import storage
from rq import get_current_job

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

app = create_app()
db.app = app

DEPOSITO = "pjecz-consultas"
SUBDIRECTORIO = "Listas de Acuerdos"


def example(seconds):
    """ Espera de n segundos """
    job = get_current_job()
    print("Iniciando tarea...")
    for sec in range(seconds):
        job.meta["progress"] = 100.0 * sec / seconds
        job.save_meta()
        print(sec)
        time.sleep(1)
    job.meta["progress"] = 100
    job.save_meta()
    print("Tarea completada.")


def construir():
    """ Construir la estructura de directorios y archivos para Pelican """


def rastrear(autoridad_id):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    print("Tarea Listas de Acuerdos/Rastrear comienza...")
    # Consultar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is False:
        return  # No es válida la autoridad
    if autoridad.listas_de_acuerdos == "":
        return  # No tiene listas de acuerdos
    print(f"- Distrito {autoridad.distrito.nombre}")
    print(f"- Autoridad {autoridad.descripcion}")
    # Consultar listas de acuerdos
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad_id == autoridad_id).all()
    fechas = [lista_de_acuerdo.fecha for lista_de_acuerdo in listas_de_acuerdos]
    print(f"- En la base de datos hay {len(fechas)} listas de acuerdos")
    # Rastrear en Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(DEPOSITO)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total = len(blobs)
    if total == 0:
        return  # No exite el subdirectorio o no tiene archivos
    print(f"- En Storage hay {total} listas de acuerdos")
    # Arrancar trabajo
    job = get_current_job()
    contador = 0
    contador_agregados = 0
    for blob in blobs:
        contador += 1
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
        job.meta["progress"] = 100.0 * contador / len(blobs)
        job.save_meta()
    print(f"- Se agregaron {contador_agregados}")
    print("Tarea Listas de Acuerdos/Rastrear terminada.")
    job.meta["progress"] = 100.0
    job.save_meta()


def respaldar():
    """ Respaldar la base de datos para descargar como archivo CSV """
