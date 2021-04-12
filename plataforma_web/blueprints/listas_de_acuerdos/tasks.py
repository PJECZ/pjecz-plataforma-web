"""
Listas de Acuerdos, tareas para ejecutar en el fondo
"""
import logging
from datetime import datetime, date
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


def set_task_progress(progress: int, mensaje: str = None):
    """ Cambiar el progreso de la tarea """
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
    """ Al fallar la tarea debe tomar el mensaje y terminarla """
    job = get_current_job()
    if job:
        job.meta["progress"] = 100
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            tarea.ha_terminado = True
            tarea.descripcion = mensaje
            tarea.save()


def agregar(autoridad_email, fecha, archivo, descripcion=None, url=None, usuario_id=None):
    """ Agregar una lista de acuerdos que se recibió vía correo electrónico """
    # Validar autoridad_email
    autoridad = Autoridad.query.filter(Autoridad.email == autoridad_email).first()
    if autoridad is False:
        mensaje = f"El e-mail {autoridad_email} no se encuentra en autoridades"
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
    # Validar fecha
    if not isinstance(fecha, date):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError as mensaje:
            mensaje = f"La fecha {str(fecha)} es incorrecta."
            bitacora.error(mensaje)
            set_task_error(mensaje)
            return mensaje
    hoy = datetime.date.today()
    pasado = hoy - datetime.timedelta(days=5)
    if fecha < pasado or fecha > hoy:
        mensaje = f"La fecha {str(fecha)} está fuera del rango de cinco días."
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
    # Validar archivo
    archivo = archivo.strip()
    if archivo == "":
        mensaje = "Está vacío el nombre de archivo."
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
    # Validar descripcion
    if descripcion is None:
        descripcion = "Lista de acuerdos"
    else:
        descripcion = descripcion.strip()
    # Validar URL
    if url is None:
        pass  # Por hacer crear URL aquí mismo
    # Si existe ese registro (autoridad, fecha) en la tabla
    lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad_id == autoridad.id).filter(ListaDeAcuerdo.fecha == fecha).first()
    if lista_de_acuerdo:
        # Actualizar
        lista_de_acuerdo.archivo = archivo
        lista_de_acuerdo.descripcion = descripcion
        lista_de_acuerdo.url = url
        mensaje = f"Actualizada la lista de acuerdos del {fecha}"
    else:
        # Insertar
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            url=url,
        )
        mensaje = f"Nueva lista de acuerdos del {fecha}"
    bitacora.info(mensaje)
    set_task_progress(100, mensaje=mensaje)
    return mensaje


def construir():
    """ Construir la estructura de directorios y archivos para Pelican """


def refrescar(autoridad_email, usuario_id=None):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    bitacora.info("Inicia listas_de_acuerdos.tasks.refrescar")
    # Validar autoridad_email
    autoridad = Autoridad.query.filter(Autoridad.email == autoridad_email).first()
    if autoridad is False:
        mensaje = f"El e-mail {autoridad_email} no se encuentra en autoridades"
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
    if autoridad.directorio_listas_de_acuerdos == "":
        mensaje = f"La autoridad {autoridad_email} no tiene directorio para listas de acuerdos"
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
    bitacora.info("- Distrito %s", autoridad.distrito.nombre)
    bitacora.info("- Autoridad %s", autoridad.descripcion)
    # Consultar listas de acuerdos
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad_id == autoridad.id).all()
    fechas = [lista_de_acuerdo.fecha for lista_de_acuerdo in listas_de_acuerdos]
    bitacora.info("- En la base de datos hay %d listas de acuerdos", len(fechas))
    # Rastrear en Google Cloud Storage
    bucket = google.cloud.storage.Client().get_bucket(DEPOSITO)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total = len(blobs)
    if total == 0:
        mensaje = "No exite el subdirectorio o no tiene archivos"
        bitacora.error(mensaje)
        set_task_error(mensaje)
        return mensaje
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
    bitacora.info("Termina listas_de_acuerdos.tasks.refrescar")
    return f"Se agregaron {contador_agregados} listas de acuerdos"


def respaldar():
    """ Respaldar la base de datos para descargar como archivo CSV """
