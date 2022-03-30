"""
Sinconizar funcionarios con la API de RRHH Personal
"""
import os
import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 4
DOCE_SEGUNDOS = 12


class ConfigurationError(Exception):
    """Error de configuración"""


class StatusCodeError(Exception):
    """Error de status code"""


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
        raise StatusCodeError(f"Error de status code: {response.status_code}")
    token = response.json()["access_token"]
    return token


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=DOCE_SEGUNDOS)
def get_personas(base_url, token, limit, offset):
    """Consultar personas"""
    response = requests.get(
        url=f"{base_url}/v1/personas",
        headers={"authorization": f"Bearer {token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        raise StatusCodeError(f"Error de status code: {response.status_code}")
    personas_response = response.json()
    return personas_response["total"], personas_response["items"]


def main():
    """Procedimiento principal"""
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)
    try:
        token = get_token(base_url, username, password)
        limit = 10
        offset = 0
        total = None
        while True:
            total, personas = get_personas(base_url, token, limit, offset)
            print(f"Voy en el offset {offset}...")
            for persona in personas:
                print(persona["nombres"], persona["apellido_primero"], persona["apellido_segundo"])
            offset += limit
            if offset >= total:
                break
    except ConfigurationError as error:
        print(f"Error de configuracion: {error}")
    except requests.ConnectionError as error:
        print(f"Error de counicacion: {error}")
    except requests.Timeout as error:
        print(f"Error de timeout: {error}")
    except StatusCodeError as error:
        print(f"Error de status code: {error}")
    return


if __name__ == "__main__":
    main()
