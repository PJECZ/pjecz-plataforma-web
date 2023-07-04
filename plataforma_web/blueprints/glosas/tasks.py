"""
Glosas, tareas para ejecutar en el fondo
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import csv

from google.cloud import storage
from rq import get_current_job
from lib.safe_string import safe_expediente

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.glosas.models import Glosa
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("glosas.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

METADATOS_CSV = "seed/glosas-metadatos.csv"


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
    bitacora.info("Termina")
    return mensaje


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las glosas para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia")

    # Para validar la fecha
    # anos_limite = 20
    # hoy = date.today()
    # hoy_dt = datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    # limite_dt = datetime(year=hoy.year - anos_limite, month=1, day=1)

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
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        return set_task_error("La autoridad no tiene directorio para glosas")
    bitacora.info("- Autoridad %s", autoridad.clave)

    # Consultar las glosas (activos e inactivos)
    glosas = Glosa.query.filter(Glosa.autoridad == autoridad).all()
    total_en_bd = len(glosas)
    bitacora.info("- Tiene %d registros en la base de datos", total_en_bd)

    # Obtener archivos en el depósito
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO_GLOSAS", "pjecz-pruebas")
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = autoridad.directorio_glosas
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)

    # Precompilar expresión regular para "NO" letras y digitos
    # letras_digitos_regex = re.compile("[^0-9a-zA-Z]+")

    # Precompilar expresión regular para hashid
    # hashid_regexp = re.compile("[0-9a-zA-Z]{8}")

    # Para descifrar los hash ids
    # hashids = Hashids(salt=os.environ.get("SALT", "Esta es una muy mala cadena aleatoria"), min_length=8)

    # Cargar metadatos de los archivos guardados en un CSV
    metadatos_csv_ruta = Path(METADATOS_CSV)
    if not metadatos_csv_ruta.exists():
        return set_task_error(f"AVISO: {metadatos_csv_ruta.name} no se encontró.")
    if not metadatos_csv_ruta.is_file():
        return set_task_error(f"AVISO: {metadatos_csv_ruta.name} no es un archivo.")
    metadatos = {}
    contador_metadatos = 0
    with open(metadatos_csv_ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            archivo_str = row["archivo"].strip()
            try:
                fecha = datetime.strptime(row["fecha"].strip(), "%Y-%m-%d").date()
            except ValueError as error:
                bitacora.warning("! METADATO INCORRECTO %s", str(error))
                continue
            try:
                expediente_str = safe_expediente(row["expediente"].strip())
            except (IndexError, ValueError):
                expediente_str = ""
            tipo_juicio_str = row["tipo_juicio"].strip()
            if tipo_juicio_str not in Glosa.TIPOS_JUICIOS.keys():
                bitacora.warning("! No se conoce el tipo de juicio %s", tipo_juicio_str)
                tipo_juicio_str = "ND"
            metadatos[archivo_str] = {
                "fecha": fecha,
                "expediente": expediente_str,
                "tipo_juicio": tipo_juicio_str,
            }
            contador_metadatos += 1
    bitacora.info("- Tiene %d metadatos", contador_metadatos)

    # Iniciar la tarea y contadores
    set_task_progress(0)
    contador_incorrectos = 0
    contador_insertados = 0
    contador_presentes = 0

    # Bucle por los archivos en el depósito
    for blob in blobs:

        # Validar que sea PDF
        ruta = Path(blob.name)
        if ruta.suffix.lower() != ".pdf":
            continue

        # Saltar y quitar de la lista si se encuentra en la consulta
        esta_en_bd = False
        for indice, glosa in enumerate(glosas):
            if blob.public_url == glosa.url:
                glosas.pop(indice)
                esta_en_bd = True
                break
        if esta_en_bd:
            contador_presentes += 1
            continue

        # Insertar
        if ruta.name in metadatos:
            encontrado = metadatos[ruta.name]
            glosa = Glosa(
                autoridad=autoridad,
                fecha=encontrado["fecha"],
                tipo_juicio=encontrado["tipo_juicio"],
                descripcion="SIN DESCRIPCION",
                expediente=encontrado["expediente"],
                archivo=ruta.name,
                url=blob.public_url,
            ).save()
            # bitacora.info("- %s", repr(glosa))
            contador_insertados += 1
        else:
            bitacora.warning("! SIN METADATOS %s", ruta.name)

    # Los registros que no se encontraron serán dados de baja
    contador_borrados = 0
    for glosa in glosas:
        if glosa.estatus == "A":
            glosa.delete()
            contador_borrados += 1

    # Mensaje final
    mensajes = []
    if contador_insertados > 0:
        mensajes.append(f"Se insertaron {contador_insertados}")
    else:
        mensajes.append("No se insertaron registros")
    if contador_borrados > 0:
        mensajes.append(f"Se borraron {contador_borrados}")
    if contador_presentes > 0:
        mensajes.append(f"Están presentes {contador_presentes}")
    if contador_incorrectos > 0:
        mensajes.append(f"Hay {contador_incorrectos} archivos con nombres incorrectos")
    mensaje_final = "- " + ". ".join(mensajes)

    # Terminar tarea
    set_task_progress(100)
    bitacora.info(mensaje_final)
    bitacora.info("Termina")
    return mensaje_final
