"""
Sentencias, tareas para ejecutar en el fondo
"""
import logging
import os
from datetime import datetime
from pathlib import Path

from dateutil.tz import tzlocal
from google.cloud import storage
from rq import get_current_job

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("sentencias.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

SUBDIRECTORIO = "Sentencias"


def set_task_progress(progress: int, mensaje: str = None):
    """Cambiar el progreso de la tarea"""
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            if progress >= 100:
                tarea.ha_terminado = True
            if mensaje is not None:
                tarea.descripcion = mensaje
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
            tarea.descripcion = mensaje
            tarea.save()
    bitacora.error(mensaje)
    bitacora.info("Termina por ERROR.")
    return mensaje


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las sentencias para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia")

    # Validad usuario
    usuario = None
    if usuario_id is not None:
        usuario = Usuario.query.get(usuario_id)
        if usuario is None or usuario.estatus != "A":
            return set_task_error("El usuario no existe o no es activo")
        bitacora.info("- Usuario %s", usuario.email)

    # Validar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        return set_task_error("La autoridad no existe o no es activa")
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        return set_task_error("La autoridad no tiene directorio para sentencias")
    bitacora.info("- Autoridad %s", autoridad.clave)

    # Consultar las sentencias (activos e inactivos) y elaborar lista de archivos
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).all()
    total_en_bd = len(sentencias)
    bitacora.info("- Tiene %d registros en la base de datos", total_en_bd)

    # Obtener archivos en el depósito
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO", "pjecz-pruebas")
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_sentencias}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)

    # Iniciar la tarea y contadores
    set_task_progress(0)
    contador_insertados = 0

    # Bucle por los archivos en el depósito
    for blob in blobs:

        # Validar que sea PDF
        ruta = Path(blob.name)
        if ruta.suffix.lower() != ".pdf":
            continue

        # Saltar y quitar de la lista si se encuentra en la consulta
        esta_en_bd = False
        for indice, sentencia in enumerate(sentencias):
            if blob.url == sentencia.url:
                sentencias.pop(indice)
                esta_en_bd = True
                break
        if esta_en_bd:
            continue

        # A partir de aquí tenemos un archivo que no está en la base de datos
        # El nombre del archivo para una sentencia debe ser como
        # AAAA-MM-DD-EEEE-EEEE-SENT-SENT-g-IDHASED.pdf

        # Tomar la fecha
        archivo_str = ruta.name
        fecha_str = archivo_str[:10]
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            bitacora.warning("X Fecha incorrecta: %s", ruta)
            continue

        # Validar la sentencia
        elementos = archivo_str[10:-4].strip("-").split("-")
        if len(elementos) >= 2:
            sentencia = elementos[0] + "/" + elementos[1]
        else:
            bitacora.warning("X Sentencia incorrecta: %s", archivo_str)
            continue

        # Validar el expediente
        if len(elementos) >= 4:
            expediente = elementos[2] + "/" + elementos[3]
        else:
            bitacora.warning("X Expediente incorrecto: %s", archivo_str)
            continue

        # Tomar la paridad de género
        if len(elementos) >= 5 and elementos[4].lower() == "g":
            es_paridad_genero = True
        else:
            es_paridad_genero = False

        # Tomar el ID hashed

        # Insertar
        tiempo_local = blob.time_created.astimezone(tzlocal())
        Sentencia(
            creado=tiempo_local,
            modificado=tiempo_local,
            autoridad=autoridad,
            fecha=fecha,
            sentencia=sentencia,
            expediente=expediente,
            es_paridad_genero=es_paridad_genero,
            archivo=archivo_str,
            url=blob.public_url,
        ).save()
        contador_insertados += 1

    # Los registros que no se encontraron serán dados de baja
    contador_borrados = 0
    for sentencia in sentencias:
        if sentencia.estatus == "A":
            sentencia.delete()
            contador_borrados += 1

    # Mensaje final
    mensajes = []
    if contador_insertados > 0:
        mensajes.append(f"Se insertaron {contador_insertados} registros")
    else:
        mensajes.append("No se insertaron registros")
    if contador_borrados > 0:
        mensajes.append(f"Se borraron {contador_borrados} registros")
    else:
        mensajes.append("No se borraron registros")
    mensaje_final = "- " + ". ".join(mensajes) + "."

    # Terminar tarea
    set_task_progress(100)
    bitacora.info(mensaje_final)
    bitacora.info("Termina")
    return mensaje_final
