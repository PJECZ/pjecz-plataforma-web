"""
CID Formatos, tareas en el fondo

- exportar_xlsx: Exportar Formatos a un archivo XLSX
"""

from datetime import datetime
import locale
import logging
import os
from pathlib import Path
import random
from typing import Tuple


from dotenv import load_dotenv
from openpyxl import Workbook
import pytz

from lib.exceptions import MyAnyError, MyEmptyError
from lib.safe_string import safe_string
from lib.storage import GoogleCloudStorage, NoneFilenameError, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

load_dotenv()  # Take environment variables from .envbitacora = logging.getLogger(__name__)

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/cid_formatos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

CLOUD_STORAGE_DEPOSITO = os.getenv("CLOUD_STORAGE_DEPOSITO", "")
DEPOSITO_DIR = "cid_formatos"
GCS_BASE_DIRECTORY = "cid_formatos/listas_maestras"
LOCAL_BASE_DIRECTORY = "exports/cid_formatos/listas_maestras"
TEMPLATES_DIR = "plataforma_web/blueprints/cid_formatos/templates/cid_formatos"
TIMEZONE = "America/Mexico_City"


def exportar_xlsx() -> Tuple[str, str, str]:
    """Exportar Lista Maestra a un archivo XLSX"""
    bitacora.info("Inicia exportar Lista Maestra a un archivo XLSX")

    # Consultar CIDFormatos
    cid_formatos = CIDFormato.query.join(CIDFormato.procedimiento).filter(CIDProcedimiento.seguimiento == "AUTORIZADO", CIDProcedimiento.estatus == "A").order_by(CIDProcedimiento.codigo, CIDProcedimiento.revision)

    # Iniciar el archivo XLSX
    libro = Workbook()

    # Tomar la hoja del libro XLSX
    hoja = libro.active

    # Agregar la fila con las cabeceras de las columnas
    hoja.append(
        [
            "CODIGO",
            "REVISION",
            "TITULO PROCEDIMIENTO",
            "DESCRIPCION",
            "AREA",
        ]
    )

    # Ajustar el ancho de las columnas
    hoja.column_dimensions["A"].width = 15
    hoja.column_dimensions["B"].width = 10
    hoja.column_dimensions["C"].width = 60
    hoja.column_dimensions["D"].width = 80
    hoja.column_dimensions["E"].width = 30

    # Inicializar el contador
    contador = 0

    # Iterar sobre los procedimientos
    for cid_formato in cid_formatos:
        # Agregar la fila con los datos
        hoja.append(
            [
                cid_formato.procedimiento.codigo,
                cid_formato.procedimiento.revision,
                safe_string(cid_formato.procedimiento.titulo_procedimiento, save_enie=True),
                cid_formato.descripcion,
                safe_string(cid_formato.procedimiento.cid_area.nombre, save_enie=True),
            ]
        )

        # Incrementar el contador
        contador += 1

    # Si el contador es 0, entonces no hay procedimientos
    if contador == 0:
        mensaje_error = "No hay formatos para exportar."
        bitacora.error(mensaje_error)
        raise MyEmptyError(mensaje_error)

    # Determinar el nombre del archivo XLSX
    ahora = datetime.now(tz=pytz.timezone(TIMEZONE))
    nombre_archivo_xlsx = f"lista_maestra_de_formatos{ahora.strftime('%Y-%m-%d_%H%M%S')}.xlsx"

    # Determinar las rutas con directorios con el año y el número de mes en dos digitos
    ruta_local = Path(LOCAL_BASE_DIRECTORY, ahora.strftime("%Y"), ahora.strftime("%m"))
    ruta_gcs = GCS_BASE_DIRECTORY  # Path(GCS_BASE_DIRECTORY, ahora.strftime("%Y"), ahora.strftime("%m"))

    # Si no existe el directorio local, crearlo
    Path(ruta_local).mkdir(parents=True, exist_ok=True)

    # Guardar el archivo XLSX
    ruta_local_archivo_xlsx = str(Path(ruta_local, nombre_archivo_xlsx))
    libro.save(ruta_local_archivo_xlsx)

    # Si esta definido el bucket de Google Cloud Storage
    public_url = ""
    if CLOUD_STORAGE_DEPOSITO != "":
        # Subir el archivo XLSX a GCS
        with open(ruta_local_archivo_xlsx, "rb") as archivo:
            storage = GoogleCloudStorage(
                base_directory=ruta_gcs,
                bucket_name=CLOUD_STORAGE_DEPOSITO,
            )
            try:
                storage.set_filename(
                    hashed_id="%08x" % random.randrange(0, 1024),
                    description="Lista Maestra de Formatos",
                    extension="xlsx",
                )
                public_url = storage.upload(archivo.read())
                bitacora.info("Se subió el archivo %s a GCS", nombre_archivo_xlsx)
            except NotConfiguredError:
                mensaje = set_task_error("No fue posible subir el archivo a Google Storage porque falta la configuración.")
                bitacora.warning(mensaje)
            except (NotAllowedExtesionError, UnknownExtesionError, NoneFilenameError) as error:
                mensaje = set_task_error("No fue posible subir el archivo a Google Storage por un error de tipo de archivo.")
                bitacora.warning(mensaje, str(error))
            except Exception as error:
                mensaje = set_task_error("No fue posible subir el archivo a Google Storage.")
                bitacora.warning(mensaje, str(error))

    # Entregar mensaje de termino, el nombre del archivo XLSX y la URL publica
    mensaje_termino = f"Se exportaron {contador} formatos a {nombre_archivo_xlsx}"
    bitacora.info(mensaje_termino)
    return mensaje_termino, nombre_archivo_xlsx, public_url


def lanzar_exportar_xlsx():
    """Lanzar exportar Lista Maestra a un archivo XLSX"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Inicia exportar Lista Maestra a un archivo XLSX")

    # Ejecutar el creador
    try:
        mensaje_termino, nombre_archivo_xlsx, public_url = exportar_xlsx()
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo y entregar el mensaje de termino
    set_task_progress(100, mensaje_termino, nombre_archivo_xlsx, public_url)
    return mensaje_termino
