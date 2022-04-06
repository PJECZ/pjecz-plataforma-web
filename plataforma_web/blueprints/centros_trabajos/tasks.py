"""
Centros de Trabajo, tareas para ejecutar en el fondo

- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
import logging
import os

from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
import requests

from lib.api_oauth2 import ConfigurationError, StatusCodeNot200Error, ResponseJSONError, get_token
from lib.safe_string import safe_clave, safe_string
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.distritos.models import Distrito

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("centros_trabajos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 2
CUATRO_SEGUNDOS = 4


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_centros_trabajos(base_url, token, limit, offset):
    """Consultar centros de trabajo"""
    response = requests.get(
        url=f"{base_url}/v1/centros_trabajos",
        headers={"authorization": f"Bearer {token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    return respuesta["total"], respuesta["items"]


def sincronizar():
    """Sincronizar funcionarios con la API de RRHH Personal"""
    # Iniciar SQLAlchemy
    app = create_app()
    app.app_context().push()
    db.app = app
    # Iniciar
    bitacora.info("Inicia sincronizar")
    # Consultar el distrito NO DEFINIDO
    distrito_no_definido = Distrito.query.filter(Distrito.nombre == "NO DEFINIDO").first()
    if distrito_no_definido is None:
        return # Error: No se encontró el distrito NO DEFINIDO
    # Tomar variables del entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL")
    username = os.getenv("RRHH_PERSONAL_API_USERNAME")
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD")
    # Bloque try/except para manejar errores
    try:
        token = get_token(base_url, username, password)
        limit = 200
        offset = 0
        total = None
        insertados_contador = 0
        actualizados_contador = 0
        while True:
            total, centros_trabajos = get_centros_trabajos(base_url, token, limit, offset)
            bitacora.info("Voy en el offset %d de %d...", offset, total)
            for centro_trabajo in centros_trabajos:
                clave = safe_clave(centro_trabajo["clave"])
                nombre = safe_string(centro_trabajo["nombre"])
                consulta = CentroTrabajo.query.filter(CentroTrabajo.clave == clave).first()
                if consulta is None:
                    # Insertar
                    CentroTrabajo(
                        clave=clave,
                        nombre=nombre,
                        telefono="ND",
                        distrito=distrito_no_definido,
                    ).save()
                    insertados_contador += 1
                elif nombre != consulta.nombre:
                    # Actualizar
                    consulta.nombre = nombre
                    consulta.save()
                    actualizados_contador += 1
            offset += limit
            if offset >= total:
                break
        bitacora.info("Se insertaron %d y se actualizaron %d centros de trabajo", insertados_contador, actualizados_contador)
    except requests.ConnectionError as error:
        bitacora.error("Error de conexion: %s", error)
    except requests.Timeout as error:
        bitacora.error("Error de falta de respuesta a tiempo: %s", error)
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        bitacora.error(error)
    # Terminado
    bitacora.info("Termino sincronizar")
    return
