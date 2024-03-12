"""
Edictos, tareas para ejecutar en el fondo
"""

import logging
import os
import re
from datetime import datetime, date
from pathlib import Path

from dateutil.tz import tzlocal
from google.cloud import storage
from hashids import Hashids
from rq import get_current_job
from lib.safe_string import safe_string
from lib.tasks import set_task_error, set_task_progress

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("edictos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear los edictos para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia")

    # Para validar la fecha
    anos_limite = 20
    hoy = date.today()
    hoy_dt = datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = datetime(year=hoy.year - anos_limite, month=1, day=1)

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
    if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
        return set_task_error("La autoridad no tiene directorio para edictos")
    bitacora.info("- Autoridad %s", autoridad.clave)

    # Consultar los edictos (activos e inactivos) y elaborar lista de archivos
    edictos = Edicto.query.filter(Edicto.autoridad == autoridad).all()
    total_en_bd = len(edictos)
    bitacora.info("- Tiene %d registros en la base de datos", total_en_bd)

    # Obtener archivos en el depósito
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO_EDICTOS", "pjecz-pruebas")
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = autoridad.directorio_edictos
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)

    # Precompilar expresión regular para "NO" letras y digitos
    letras_digitos_regex = re.compile("[^0-9a-zA-Z]+")

    # Precompilar expresión regular para hashid
    hashid_regexp = re.compile("[0-9a-zA-Z]{8}")

    # Para descifrar los hash ids
    hashids = Hashids(salt=os.environ.get("SALT", "Esta es una muy mala cadena aleatoria"), min_length=8)

    # Iniciar tarea
    mensaje_inicial = "Inicia refrescar los Edictos"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

    # Iniciar contadores
    contador_incorrectos = 0
    contador_insertados = 0
    contador_presentes = 0

    # Bucle por los archivos en el depósito
    for blob in blobs:

        # Saltar si no es un archivo PDF
        ruta = Path(blob.name)
        if ruta.suffix.lower() != ".pdf":
            continue

        # Saltar y quitar de la lista si se encuentra en la consulta
        esta_en_bd = False
        for indice, edicto in enumerate(edictos):
            if blob.public_url == edicto.url:
                edictos.pop(indice)
                esta_en_bd = True
                break
        if esta_en_bd:
            contador_presentes += 1
            continue

        # A partir de aquí tenemos un archivo que no está en la base de datos
        # El nombre del archivo para un edicto debe ser como
        # AAAA-MM-DD-EEEE-EEEE-NUMP-NUMP-DESCRIPCION-BLA-BLA-IDHASED.pdf

        # Separar elementos del nombre del archivo
        nombre_sin_extension = ruta.name[:-4]
        elementos = re.sub(letras_digitos_regex, "-", nombre_sin_extension).strip("-").split("-")

        # Tomar la fecha
        try:
            ano = int(elementos.pop(0))
            mes = int(elementos.pop(0))
            dia = int(elementos.pop(0))
            fecha = date(ano, mes, dia)
        except (IndexError, ValueError):
            bitacora.warning("X Fecha incorrecta: %s", ruta)
            contador_incorrectos += 1
            continue

        # Descartar fechas en el futuro o muy en el pasado
        if not limite_dt <= datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            bitacora.warning("X Fecha fuera de rango: %s", ruta)
            contador_incorrectos += 1
            continue

        # Tomar el expediente
        try:
            numero = int(elementos[0])
            ano = int(elementos[1])
            expediente = str(numero) + "/" + str(ano)
            elementos.pop(0)
            elementos.pop(0)
        except (IndexError, ValueError):
            expediente = None

        # Tomar el número publicación
        try:
            numero = int(elementos[0])
            ano = int(elementos[1])
            numero_publicacion = str(numero) + "/" + str(ano)
            elementos.pop(0)
            elementos.pop(0)
        except (IndexError, ValueError):
            numero_publicacion = None

        # Tomar la descripción, sin el hash del id de estar presente
        if len(elementos) > 1:
            if re.match(hashid_regexp, elementos[-1]) is None:
                descripcion = safe_string(" ".join(elementos))
            else:
                decodificado = hashids.decode(elementos[-1])
                if isinstance(decodificado, tuple) and len(decodificado) > 0:
                    descripcion = safe_string(" ".join(elementos[:-1]))
                else:
                    descripcion = safe_string(" ".join(elementos))
        else:
            descripcion = "SIN DESCRIPCION"

        # Insertar
        tiempo_local = blob.time_created.astimezone(tzlocal())
        Edicto(
            creado=tiempo_local,
            modificado=tiempo_local,
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            expediente=expediente,
            numero_publicacion=numero_publicacion,
            archivo=ruta.name,
            url=blob.public_url,
        ).save()
        contador_insertados += 1

    # Los registros que no se encontraron serán dados de baja
    contador_borrados = 0
    for edicto in edictos:
        if edicto.estatus == "A":
            edicto.delete()
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
    if contador_presentes > 0:
        mensajes.append(f"Están presentes {contador_presentes}")
    if contador_incorrectos > 0:
        mensajes.append(f"Hay {contador_incorrectos} archivos con nombres incorrectos")
    mensaje_final = "- " + ". ".join(mensajes) + "."

    # Terminar tarea
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final
