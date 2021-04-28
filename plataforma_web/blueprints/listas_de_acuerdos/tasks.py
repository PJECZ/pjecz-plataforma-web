"""
Listas de Acuerdos, tareas para ejecutar en el fondo
"""
import logging
from datetime import datetime
from pathlib import Path
from unidecode import unidecode

import google.cloud.storage
from rq import get_current_job

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
empunadura = logging.FileHandler("listas_de_acuerdos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

# DEPOSITO = current_app.config["CLOUD_STORAGE_DEPOSITO"]
DEPOSITO = "pjecz-pruebas"
SUBDIRECTORIO = "Listas de Acuerdos"


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
    return mensaje


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las listas de acuerdos para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia listas_de_acuerdos.tasks.refrescar")
    # Validad usuario
    usuario = None
    if usuario_id is None:
        bitacora.info("- Usuario no definido")
    else:
        usuario = Usuario.query.get(usuario_id)
        if usuario is None or usuario.estatus != "A":
            return set_task_error("El usuario no existe o no es activo")
        bitacora.info("- Usuario %s", usuario.email)
    # Validar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        return set_task_error("La autoridad no existe o no es activa")
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        return set_task_error("La autoridad no tiene directorio para listas de acuerdos")
    bitacora.info("- Autoridad %s", autoridad.clave)
    # Consultar las listas de acuerdos en la base de datos
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).all()
    total_en_bd = len(listas_de_acuerdos)
    bitacora.info("- En BD hay %d listas de acuerdos", total_en_bd)
    fechas = [lista_de_acuerdo.fecha for lista_de_acuerdo in listas_de_acuerdos]
    # Obtener archivos en el depósito
    bucket = google.cloud.storage.Client().get_bucket(DEPOSITO)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- En Storage hay %d archivos", total_en_deposito)
    # Poner el progreso de la tarea y los contadores en cero
    set_task_progress(0)
    contador_insertados = 0
    # Bucle por los archivos en el depósito
    for blob in blobs:
        ruta = Path(blob.name)
        archivo_str = ruta.name
        # A partir del nombre del archivo
        fecha_str = archivo_str[:10]
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            bitacora.warning("X Fecha incorrecta: %s", ruta)
            continue
        if ruta.suffix.lower() != ".pdf":
            bitacora.warning("X No es PDF: %s", ruta)
            continue
        if len(archivo_str) > 14:  # YYYY-MM-DD.pdf
            descripcion = unidecode(archivo_str[11:-4]).strip().upper()
        else:
            descripcion = ""
        # Si ya existe esa fecha en la BD
        esta_en_bd = True
        try:
            posicion = fechas.index(fecha)
            fechas.pop(posicion)
        except ValueError:
            esta_en_bd = False
        # Insertar
        if not esta_en_bd:
            ListaDeAcuerdo(
                creado=blob.time_created,
                modificado=blob.time_created,
                autoridad=autoridad,
                fecha=fecha,
                archivo=archivo_str,
                descripcion=descripcion,
                url=blob.public_url,
            ).save()
            contador_insertados += 1
    # Bucle por las fechas que quedaron sin encontrarse
    contador_borrados = 0
    for fecha in fechas:
        lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.fecha == fecha).first()
        if lista_de_acuerdo:
            lista_de_acuerdo.delete()
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
    bitacora.info("Termina listas_de_acuerdos.tasks.refrescar")
    return mensaje_final


""" def agregar(autoridad_email, fecha, archivo, descripcion=None, url=None, usuario_id=None):
    Agregar una lista de acuerdos que se recibió vía correo electrónico
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
 """
