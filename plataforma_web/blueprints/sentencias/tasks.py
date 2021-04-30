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
    bitacora.info("Termina por ERROR sentencias.tasks.refrescar")
    return mensaje


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las sentencias para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia sentencias.tasks.refrescar")
    # Configuración
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO", "pjecz-pruebas")
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
    # Obtener los nombres de los archivos de las sentencias en BD
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).all()
    total_en_bd = len(sentencias)
    bitacora.info("- Tiene %d sentencias en la base de datos", total_en_bd)
    archivos = [sentencia.archivo for sentencia in sentencias]
    # Obtener archivos en el depósito
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_sentencias}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)
    # Poner el progreso de la tarea y los contadores en cero
    set_task_progress(0)
    contador_insertados = 0
    # Bucle por los archivos en el depósito
    for blob in blobs:
        # Validar que sea PDF
        ruta = Path(blob.name)
        if ruta.suffix.lower() != ".pdf":
            continue
        # Validar la fecha
        archivo_str = ruta.name
        fecha_str = archivo_str[:10]
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            bitacora.warning("X Fecha incorrecta: %s", ruta)
            continue
        # Tomar la sentencia
        elementos = archivo_str[10:-4].strip("-").split("-")
        if len(elementos) >= 2:
            sentencia = elementos[0] + "/" + elementos[1]
        else:
            bitacora.warning("X Sentencia incorrecta: %s", archivo_str)
            continue
        # Tomar el expediente
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
        # Si ya existe ese archivo en la BD
        esta_en_bd = True
        try:
            posicion = archivos.index(archivo_str)
            archivos.pop(posicion)  # Se saca de la lista
        except ValueError:
            esta_en_bd = False
        # Insertar
        if not esta_en_bd:
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
    # Bucle por los archivos que quedaron sin encontrarse
    contador_borrados = 0
    for archivo_str in archivos:
        sentencia = Sentencia.query.filter(Sentencia.archivo == archivo_str).first()
        if sentencia:
            sentencia.delete()  # Dar de baja porque no está en el depósito
            contador_borrados += 1
    # Mensaje final
    resultados = []
    if contador_insertados > 0:
        resultados.append(f"Se insertaron {contador_insertados} registros")
    else:
        resultados.append("No se insertaron registros")
    if contador_borrados > 0:
        resultados.append(f"Se borraron {contador_borrados} registros")
    else:
        resultados.append("No se borraron registros")
    mensaje_final = "- " + ". ".join(resultados) + "."
    # Terminar tarea
    set_task_progress(100)
    bitacora.info(mensaje_final)
    bitacora.info("Termina sentencias.tasks.refrescar")
    return mensaje_final
