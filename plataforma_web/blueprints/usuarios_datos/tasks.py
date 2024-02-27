"""
Usuarios Datos, tareas en el fondo
"""

import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pytz
from openpyxl import Workbook

from lib.exceptions import (
    MyAnyError,
    MyBucketNotFoundError,
    MyEmptyError,
    MyFileNotAllowedError,
    MyFileNotFoundError,
    MyUploadError,
)
from lib.storage import GoogleCloudStorage, NoneFilenameError, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.tasks import set_task_error, set_task_progress
from plataforma_web.app import create_app
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato
from plataforma_web.extensions import db

GCS_BASE_DIRECTORY = "usuarios_datos/exportaciones"
LOCAL_BASE_DIRECTORY = "exports/usuarios_datos"
TIMEZONE = "America/Mexico_City"

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/usuarios_datos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app


def exportar_xlsx() -> Tuple[str, str, str]:
    """Exportar Usuarios-Datos a un archivo XLSX"""
    bitacora.info("Inicia exportar Usuarios Datos a un archivo XLSX")

    # Tomar el nombre del bucket de Google Cloud Storage donde se va a subir el archivo
    bucket_name = os.getenv("CLOUD_STORAGE_DEPOSITO_USUARIOS", "")

    # Consultar Usuarios-Datos
    usuarios_datos = UsuarioDato.query.join(Usuario).filter(UsuarioDato.estatus == "A").order_by(UsuarioDato.curp).all()

    # Iniciar el archivo XLSX
    libro = Workbook()

    # Tomar la hoja del libro XLSX
    hoja = libro.active

    # Agregar la fila con las cabeceras de las columnas
    hoja.append(
        [
            "CURP",
            "NOMBRES",
            "APELLIDO PRIMERO",
            "APELLIDO SEGUNDO",
            "FECHA NACIMIENTO",
            "ESTADO GENERAL",
            "CP FISCAL",
            "DOMICILIO CALLE",
            "DOMICILIO NUMERO EXT",
            "DOMICILIO NUMERO INT",
            "DOMICILIO COLONIA",
            "DOMICILIO CIUDAD",
            "DOMICILIO ESTADO",
            "DOMICILIO CP",
            "ES MADRE",
            "ESTADO CIVIL",
            "ESTUDIOS CEDULA",
            "EMAIL PERSONAL",
            "TELEFONO CELULAR",
        ]
    )

    # Inicializar el contador
    contador = 0

    # Iterar sobre los Usuarios-Datos
    for usuario_dato in usuarios_datos:
        # Agregar la fila con los datos del usuario-dato
        hoja.append(
            [
                usuario_dato.curp,
                usuario_dato.usuario.nombres,
                usuario_dato.usuario.apellido_paterno,
                usuario_dato.usuario.apellido_materno,
                usuario_dato.fecha_nacimiento,
                usuario_dato.estado_general,
                usuario_dato.cp_fiscal,
                usuario_dato.domicilio_calle,
                usuario_dato.domicilio_numero_ext,
                usuario_dato.domicilio_numero_int,
                usuario_dato.domicilio_colonia,
                usuario_dato.domicilio_ciudad,
                usuario_dato.domicilio_estado,
                usuario_dato.domicilio_cp,
                usuario_dato.es_madre,
                usuario_dato.estado_civil,
                usuario_dato.estudios_cedula,
                usuario_dato.usuario.email_personal,
                usuario_dato.usuario.telefono_celular,
            ]
        )

        # Incrementar el contador
        contador += 1

    # Si el contador es 0, entonces no hay Usuarios-Datos
    if contador == 0:
        mensaje_error = "No hay Usuarios-Datos para exportar."
        bitacora.error(mensaje_error)
        raise MyEmptyError(mensaje_error)

    # Determinar el nombre del archivo XLSX
    ahora = datetime.now(tz=pytz.timezone(TIMEZONE))
    nombre_archivo_xlsx = f"documentos_personales_{ahora.strftime('%Y-%m-%d_%H%M%S')}.xlsx"

    # Determinar las rutas con directorios con el año y el número de mes en dos digitos
    ruta_local = Path(LOCAL_BASE_DIRECTORY, ahora.strftime("%Y"), ahora.strftime("%m"))
    ruta_gcs = GCS_BASE_DIRECTORY  # Path(GCS_BASE_DIRECTORY, ahora.strftime("%Y"), ahora.strftime("%m"))

    # Si no existe el directorio local, crearlo
    Path(ruta_local).mkdir(parents=True, exist_ok=True)

    # Guardar el archivo XLSX
    ruta_local_archivo_xlsx = str(Path(ruta_local, nombre_archivo_xlsx))
    libro.save(ruta_local_archivo_xlsx)

    # Si esta definido el bucket de Google Cloud Storage
    if bucket_name != "":
        # Subir el archivo XLSX a GCS
        with open(ruta_local_archivo_xlsx, "rb") as archivo:
            storage = GoogleCloudStorage(
                base_directory=ruta_gcs,
                bucket_name=bucket_name,
            )
            try:
                storage.set_filename(
                    hashed_id="%08x" % random.randrange(0, 1024),
                    description="Documentos-Personales",
                    extension="xlsx",
                )
                storage.upload(archivo.read())
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
    mensaje_termino = f"Se exportaron {contador} Usuarios-Datos a {nombre_archivo_xlsx}"
    bitacora.info(mensaje_termino)
    return mensaje_termino, nombre_archivo_xlsx, ""


def lanzar_exportar_xlsx():
    """Exportar Usuarios-Datos a un archivo XLSX"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Inicia exportar Usuarios-Datos a un archivo XLSX")

    # Ejecutar el creador
    try:
        mensaje_termino, nombre_archivo_xlsx, public_url = exportar_xlsx()
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo y entregar el mensaje de termino
    set_task_progress(100, mensaje_termino)  # nombre_archivo_xlsx, public_url
    return mensaje_termino
