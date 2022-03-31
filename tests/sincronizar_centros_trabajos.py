"""
Sinconizar centros de trabajos con la API de RRHH Personal
"""
import os
import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from tabulate import tabulate

from lib.safe_string import safe_clave, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.distritos.models import Distrito

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 2
CUATRO_SEGUNDOS = 4


class ConfigurationError(Exception):
    """Error de configuración"""


class StatusCodeNot200Error(Exception):
    """Error de status code"""


class ResponseJSONError(Exception):
    """Error de respuesta JSON"""


def get_token(base_url, username, password):
    """Iniciar sesion y obtener token"""
    if base_url is None or username is None or password is None:
        raise ConfigurationError("Falta configurar las variables de entorno")
    response = requests.post(
        url=f"{base_url}/token",
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "access_token" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el token")
    return respuesta["access_token"]


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


def main():
    """Procedimiento principal"""
    # Iniciar SQLAlchemy
    app = create_app()
    app.app_context().push()
    db.app = app
    # Consultar el distrito NO DEFINIDO
    distrito_no_definido = Distrito.query.filter(Distrito.nombre == "NO DEFINIDO").first()
    if distrito_no_definido is None:
        print("Error: No se encontró el distrito NO DEFINIDO")
        return
    # Obtener variables de entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)
    try:
        token = get_token(base_url, username, password)
        limit = 10
        offset = 0
        total = None
        insertados_contador = 0
        actualizados_contador = 0
        while True:
            total, centros_trabajos = get_centros_trabajos(base_url, token, limit, offset)
            print(f"Voy en el offset {offset} de {total}...")
            datos = []
            for centro_trabajo in centros_trabajos:
                accion = ""
                clave = safe_clave(centro_trabajo["clave"])
                nombre = safe_string(centro_trabajo["nombre"])
                consulta = CentroTrabajo.query.filter(CentroTrabajo.clave == clave).first()
                if consulta is None:
                    accion = "Insertado"
                    CentroTrabajo(
                        clave=clave,
                        nombre=nombre,
                        telefono="ND",
                        distrito=distrito_no_definido,
                    ).save()
                    insertados_contador += 1
                elif nombre != consulta.nombre:
                    accion = "Actualizado"
                    consulta.nombre = nombre
                    consulta.save()
                    actualizados_contador += 1
                datos.append([clave, nombre, accion])
            print(tabulate(datos, headers=["Clave", "Nombre", "Acción"]))
            offset += limit
            if offset >= total:
                break
        print(f"Se insertaron {insertados_contador} y se actualizaron {actualizados_contador} centros de trabajo")
    except requests.ConnectionError as error:
        print(f"Error de conexion: {error}")
    except requests.Timeout as error:
        print(f"Error de falta de respuesta a tiempo: {error}")
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        print(error)
    return


if __name__ == "__main__":
    main()
