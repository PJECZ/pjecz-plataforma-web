"""
Funcionarios, tareas para ejecutar en el fondo

- asignar_oficinas: Asignar funcionarios_oficinas a partir de una direccion
- limpiar_oficinas: Limpiar funcionarios_oficinas
- enviar_reporte: Enviar via correo electronico el reporte de funcionarios
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
from datetime import datetime, date
import locale
import logging
import os

from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
import requests

from lib.tasks import set_task_progress, set_task_error
from lib.safe_string import safe_clave, safe_email, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.domicilios.models import Domicilio
from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.funcionarios_oficinas.models import FuncionarioOficina
from plataforma_web.blueprints.oficinas.models import Oficina

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("funcionarios.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

INGRESO_FECHA_POR_DEFECTO = datetime(2000, 1, 1)

LIMITE_CANTIDAD = 40
LLAMADOS_CANTIDAD = 20
ESPERA_SEGUNDOS = 4


def asignar_oficinas(funcionario_id: int, domicilio_id: int):
    """Asignar funcionarios_oficinas a partir de una direccion"""

    # Iniciar
    bitacora.info("Inicia asignar oficinas")

    # Consultar funcionario
    funcionario = Funcionario.query.get(funcionario_id)
    if funcionario is None:
        mensaje = "No se encuentra al funcionario"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Consultar domicilio
    domicilio = Domicilio.query.get(domicilio_id)
    if domicilio is None:
        mensaje = "No se encuentra al domicilio"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Consultar las oficinas activas de ese domicilio
    oficinas = Oficina.query.filter(Oficina.domicilio == domicilio).filter(Oficina.estatus == "A").all()

    # Insertar o actualizar los registros de funcionarios_oficinas
    contador = 0
    for oficina in oficinas:
        funcionario_oficina = FuncionarioOficina.query.filter(FuncionarioOficina.funcionario == funcionario).filter(FuncionarioOficina.oficina == oficina).first()
        if funcionario_oficina is None:
            # No existe, vamos a insertar
            FuncionarioOficina(
                funcionario=funcionario,
                oficina=oficina,
                descripcion=f"Funcionario {funcionario.curp} en {oficina.clave}",
            ).save()
            contador += 1
        else:
            # Si existe, vamos a actualizar si esta eliminado
            if funcionario_oficina.estatus != "A":
                funcionario_oficina.estatus = "A"
                funcionario_oficina.save()
                contador += 1

    # Terminar
    set_task_progress(100)
    mensaje_final = f"Terminado asignar {contador} oficinas al CURP {funcionario.curp}"
    bitacora.info(mensaje_final)
    return mensaje_final


def limpiar_oficinas(funcionario_id: int):
    """Limpiar funcionarios_oficinas"""

    # Iniciar
    bitacora.info("Inicia limpiar oficinas")

    # Consultar funcionario
    funcionario = Funcionario.query.get(funcionario_id)
    if funcionario is None:
        mensaje = "No se encuentra al funcionario"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Limpiar (cambiar estatus a B) los registros de funcionarios_oficinas
    contador = 0
    for funcionario_oficina in FuncionarioOficina.query.filter(FuncionarioOficina.funcionario == funcionario).all():
        if funcionario_oficina.estatus == "A":
            funcionario_oficina.delete()
            contador += 1

    # Terminar
    set_task_progress(100)
    mensaje_final = f"Terminado limpiar oficinas, {contador} a {funcionario.curp}"
    bitacora.info(mensaje_final)
    return mensaje_final


def enviar_reporte():
    """Enviar reporte de funcionarios via correo electronico"""

    # Iniciar
    bitacora.info("Inicia enviar reporte")

    # Consultar
    funcionarios = db.session.query(Funcionario).filter_by(estatus="A")
    bitacora.info("Hay %s funcionarios activos", funcionarios.count())

    # Terminar
    set_task_progress(100)
    mensaje_final = "Terminado enviar reporte satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final


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
@limits(calls=LLAMADOS_CANTIDAD, period=ESPERA_SEGUNDOS)
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
@limits(calls=LLAMADOS_CANTIDAD, period=ESPERA_SEGUNDOS)
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
@limits(calls=LLAMADOS_CANTIDAD, period=ESPERA_SEGUNDOS)
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
@limits(calls=LLAMADOS_CANTIDAD, period=ESPERA_SEGUNDOS)
def get_personas_fotografias(base_url, token, persona_id):
    """Consultar fotografias de las personas, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/personas_fotografias",
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


def sincronizar():
    """Sincronizar funcionarios con la API de RRHH Personal"""

    # Iniciar
    bitacora.info("Inicia sincronizar")

    # Consultar el centro de trabajo NO DEFINIDO
    centro_trabajo_no_definido = CentroTrabajo.query.filter_by(nombre="NO DEFINIDO").first()
    if centro_trabajo_no_definido is None:
        mensaje_error = "No se encontro el centro de trabajo NO DEFINIDO"
        bitacora.error(mensaje_error)
        return

    # Obtener variables de entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)

    # Bloque try/except para manejar errores
    try:
        token = get_token(base_url, username, password)
        offset = 0
        total = None
        insertados_contador = 0
        actualizados_contador = 0

        # Bucle para hacer las consultas hasta que se acaben las personas
        while True:
            total, personas = get_personas(base_url, token, LIMITE_CANTIDAD, offset)
            bitacora.info(f"Voy en el offset {offset} de {total}...")
            for persona in personas:
                en_funciones = True

                # Datos de personas
                persona_id = int(persona["id"])
                nombres = safe_string(persona["nombres"])
                apellido_paterno = safe_string(persona["apellido_primero"])
                apellido_materno = safe_string(persona["apellido_segundo"])
                nombre = f"{nombres} {apellido_paterno} {apellido_materno}"
                if nombres == "" or apellido_paterno == "":
                    bitacora.warning("Se omite %s (%d) porque falta el nombre o el primer apellido", nombre, persona_id)
                    continue
                curp = safe_string(persona["curp"], max_len=18)
                if curp == "":
                    bitacora.warning("Se omite %s (%d) porque falta o es incorrecto el CURP", nombre, persona_id)
                    continue
                email = safe_email(persona["email"])
                if email == "":
                    bitacora.warning("Se omite %s (%d) porque falta el email", nombre, persona_id)
                    continue
                if not email.endswith("@coahuila.gob.mx"):
                    bitacora.warning("Se omite %s (%d) porque el email %s no es de coahuila.gob.mx", nombre, persona_id, email)
                    continue
                if persona["situacion"] == "B":
                    bitacora.info("A %s (%d) esta en Baja por lo que NO esta en funciones", nombre, persona_id)
                    en_funciones = False
                if persona["situacion"] == "A.D.SUS":
                    bitacora.info("A %s (%d) esta Suspendida por lo que NO esta en funciones", nombre, persona_id)
                    en_funciones = False
                if persona["fecha_ingreso_pj"] is not None:
                    ingreso_fecha = datetime.strptime(persona["fecha_ingreso_pj"], "%Y-%m-%d").date()
                else:
                    bitacora.info("A %s (%d) se le define una fecha de ingreso por defecto", nombre, persona_id)
                    ingreso_fecha = date(1900, 1, 1)

                # Datos de historial de puestos
                puesto = ""
                puesto_clave = ""
                centro_trabajo_clave = ""
                historial_puesto = get_historial_puestos(base_url, token, persona_id)
                if historial_puesto is None:
                    bitacora.info("A %s (%d) NO tiene historial de puestos por lo que NO esta en funciones", nombre, persona_id)
                    en_funciones = False
                if en_funciones and historial_puesto["fecha_termino"] is None:  # La fecha de termino vacia significa que esta en funciones
                    puesto = safe_string(historial_puesto["puesto_funcion_nombre"])
                    centro_trabajo_clave = safe_clave(historial_puesto["centro_trabajo"])
                    # Datos del puesto
                    puesto_funcion = get_puesto_funcion(base_url, token, historial_puesto["puesto_funcion_id"])
                    puesto_clave = safe_clave(puesto_funcion["puesto_clave"])
                else:
                    bitacora.info("A %s (%d) NO tiene un historial de puesto abierto por lo que NO esta en funciones", nombre, persona_id)
                    en_funciones = False

                # Datos de fotografias
                fotografia_url = ""
                fotografia = get_personas_fotografias(base_url, token, persona_id)
                if fotografia and (fotografia["url"] is not None or fotografia["url"] != ""):
                    fotografia_url = fotografia["url"]

                # Decidir entre insertar o actualizar
                funcionario = Funcionario.query.filter_by(curp=curp).first()
                if funcionario is None:
                    funcionario_con_mismo_email = Funcionario.query.filter_by(email=email).first()
                    if funcionario_con_mismo_email is not None:
                        bitacora.warning("Se omite insertar %s (%d) porque el email %s ya esta registrado", nombre, persona_id, email)
                        continue
                    centro_trabajo = CentroTrabajo.query.filter_by(clave=centro_trabajo_clave).first()
                    if centro_trabajo is None:
                        centro_trabajo = centro_trabajo_no_definido
                    Funcionario(
                        centro_trabajo=centro_trabajo,
                        nombres=nombres,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        curp=curp,
                        email=email,
                        puesto=puesto,
                        puesto_clave=puesto_clave,
                        ingreso_fecha=ingreso_fecha,
                        fotografia_url=fotografia_url,
                        en_funciones=en_funciones,
                    ).save()
                    insertados_contador += 1
                else:
                    ha_cambiado = False
                    if email != funcionario.email:
                        funcionario_con_mismo_email = Funcionario.query.filter_by(email=email).first()
                        if funcionario_con_mismo_email is not None:
                            bitacora.warning("Se omite actualizar %s (%d) porque el email %s ya esta registrado", nombre, persona_id, email)
                            continue
                        ha_cambiado = True
                        funcionario.email = email
                    if nombres != funcionario.nombres:
                        ha_cambiado = True
                        funcionario.nombres = nombres
                    if apellido_paterno != funcionario.apellido_paterno:
                        ha_cambiado = True
                        funcionario.apellido_paterno = apellido_paterno
                    if apellido_materno != funcionario.apellido_materno:
                        ha_cambiado = True
                        funcionario.apellido_materno = apellido_materno
                    if puesto != funcionario.puesto:
                        ha_cambiado = True
                        funcionario.puesto = puesto
                    if puesto_clave != funcionario.puesto_clave:
                        ha_cambiado = True
                        funcionario.puesto_clave = puesto_clave
                    if ingreso_fecha != funcionario.ingreso_fecha:
                        ha_cambiado = True
                        funcionario.ingreso_fecha = ingreso_fecha
                    if fotografia_url != funcionario.fotografia_url:
                        ha_cambiado = True
                        funcionario.fotografia_url = fotografia_url
                    if en_funciones != funcionario.en_funciones:
                        ha_cambiado = True
                        funcionario.en_funciones = en_funciones
                    if ha_cambiado:
                        funcionario.save()
                        actualizados_contador += 1

            # Definir offset para el siguiente bloque de personas
            offset += LIMITE_CANTIDAD

            # Terminar bucle while cuando no hay mas personas
            if offset >= total:
                break

        mensaje_final = f"Se insertaron {insertados_contador} y se actualizaron {actualizados_contador} funcionarios"
        bitacora.info("Termina. %s", mensaje_final)
        bitacora.info(mensaje_final)
    except requests.ConnectionError as error:
        bitacora.error(f"Error de conexion: {error}")
    except requests.Timeout as error:
        bitacora.error(f"Error de falta de respuesta a tiempo: {error}")
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        bitacora.error(error)

    # Terminar
    bitacora.info("Terminado sincronizar satisfactoriamente")
    return
