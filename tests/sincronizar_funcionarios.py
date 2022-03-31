"""
Sinconizar funcionarios con la API de RRHH Personal
"""
from datetime import datetime, date
import os

from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
import requests
from tabulate import tabulate

from lib.safe_string import safe_clave, safe_email, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 12
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
def get_personas(base_url, token, limit, offset):
    """Consultar personas"""
    response = requests.get(
        url=f"{base_url}/v1/personas",
        headers={"authorization": f"Bearer {token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    return respuesta["total"], respuesta["items"]


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_historial_puestos(base_url, token, persona_id):
    """Consultar historial de puestos, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/historial_puestos",
        headers={"authorization": f"Bearer {token}"},
        params={"persona_id": persona_id, "limit": 1, "offset": 0},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    if respuesta["total"] > 0:
        return respuesta["items"][0]  # Entrega el unico elemento del listado
    return None


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_puesto_funcion(base_url, token, puesto_funcion_id):
    """Consultar un puesto funcion"""
    response = requests.get(
        url=f"{base_url}/v1/puestos_funciones/{puesto_funcion_id}",
        headers={"authorization": f"Bearer {token}"},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    return response.json()


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_personas_domicilios(base_url, token, persona_id):
    """Consultar domicilios de las personas, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/personas_domicilios",
        headers={"authorization": f"Bearer {token}"},
        params={"persona_id": persona_id, "limit": 1, "offset": 0},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    if respuesta["total"] > 0:
        return respuesta["items"][0]  # Entrega el unico elemento del listado
    return None


def main():
    """Procedimiento principal"""
    # Iniciar SQLAlchemy
    app = create_app()
    app.app_context().push()
    db.app = app
    # Obtener variables de entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)
    # Bloque try/except para manejar errores
    try:
        token = get_token(base_url, username, password)
        limit = 10
        offset = 0
        total = None
        insertados_contador = 0
        actualizados_contador = 0
        while True:
            total, personas = get_personas(base_url, token, limit, offset)
            print(f"Voy en el offset {offset} de {total}...")
            datos = []
            for persona in personas:
                accion = ""
                # Datos de personas
                persona_id = int(persona["id"])
                nombres = safe_string(persona["nombres"])
                apellido_paterno = safe_string(persona["apellido_primero"])
                apellido_materno = safe_string(persona["apellido_segundo"])
                nombre = f"{nombres} {apellido_paterno} {apellido_materno}"
                curp = safe_string(persona["curp"], max_len=18)
                email = safe_email(persona["email"])
                if persona["fecha_ingreso_pj"] is not None:
                    ingreso_fecha = datetime.strptime(persona["fecha_ingreso_pj"], "%Y-%m-%d").date()
                else:
                    ingreso_fecha = date(1900, 1, 1)
                # Datos de historial de puestos
                puesto = ""
                puesto_clave = ""
                centro_trabajo_clave = ""
                historial_puesto = get_historial_puestos(base_url, token, persona_id)
                if historial_puesto and historial_puesto["fecha_termino"] is None:  # La fecha de termino vacia significa que esta activo
                    puesto = safe_string(historial_puesto["puesto_funcion_nombre"])
                    centro_trabajo_clave = safe_clave(historial_puesto["centro_trabajo"])
                    # Datos del puesto
                    puesto_funcion = get_puesto_funcion(base_url, token, historial_puesto["puesto_funcion_id"])
                    puesto_clave = safe_clave(puesto_funcion["puesto_clave"])
                # Datos de personas domicilios
                domicilio_oficial = ""
                domicilio = get_personas_domicilios(base_url, token, persona_id)
                if domicilio:
                    calle = safe_string(domicilio["calle"])
                    numero_exterior = safe_string(domicilio["numero_exterior"])
                    numero_interior = safe_string(domicilio["numero_interior"])
                    colonia = safe_string(domicilio["colonia"])
                    municipio = safe_string(domicilio["municipio"])
                    entidad = safe_string(domicilio["entidad"])
                    # pais = safe_string(domicilio["pais"])
                    codigo_postal = int(domicilio["codigo_postal"])
                    elementos = []
                    if calle and numero_exterior and numero_interior:
                        elementos.append(f"{calle} #{numero_exterior}-{numero_interior}")
                    elif calle and numero_exterior:
                        elementos.append(f"{calle} #{numero_exterior}")
                    elif calle:
                        elementos.append(calle)
                    if colonia:
                        elementos.append(colonia)
                    if municipio:
                        elementos.append(municipio)
                    if entidad and codigo_postal > 0:
                        elementos.append(f"{entidad}, C.P. {codigo_postal}")
                    elif entidad:
                        elementos.append(entidad)
                    domicilio_oficial = ", ".join(elementos)
                # Acumular datos
                datos.append([nombre[:24], curp, email[:16], ingreso_fecha, centro_trabajo_clave, puesto_clave, puesto[:24], domicilio_oficial[:64]])
            print(tabulate(datos, headers=["Nombre", "CURP", "Email", "Ingreso", "Centro de trabajo", "Clave del puesto", "Puesto", "Dom. oficial"]))
            offset += limit
            if offset >= total:
                break
    except requests.ConnectionError as error:
        print(f"Error de conexion: {error}")
    except requests.Timeout as error:
        print(f"Error de falta de respuesta a tiempo: {error}")
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        print(error)
    return


if __name__ == "__main__":
    main()
