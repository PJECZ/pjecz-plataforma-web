"""
Funcionarios, tareas para ejecutar en el fondo

- asignar_oficinas: Asignar funcionarios_oficinas a partir de una direccion
- limpiar_oficinas: Limpiar funcionarios_oficinas
- enviar_reporte: Enviar via correo electronico el reporte de funcionarios
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
import locale
import logging
import os
import requests

from dotenv import load_dotenv
from sqlalchemy import or_

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.funcionarios_oficinas.models import FuncionarioOficina

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


def asignar_oficinas(funcionario_id: int, domicilio_id: int):
    """Asignar funcionarios_oficinas a partir de una direccion"""

    # Iniciar
    bitacora.info("Inicia asignar oficinas")

    # Terminar
    set_task_progress(100)
    mensaje_final = "Terminado asignar oficinas"
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
            contador +=1

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


def sincronizar():
    """Sincronizar funcionarios con la API de RRHH Personal"""

    # Iniciar
    bitacora.info("Inicia sincronizar")

    # Iniciar sesion
    base_url = os.getenv("RRHH_PERSONAL_API_URL")
    username = os.getenv("RRHH_PERSONAL_API_USERNAME")
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD")
    response = requests.post(
        url=f"{base_url}/token",
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        mensaje = f"Fallo el inicio de sesion con error {response.status_code}"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return
    token = response.json()["access_token"]
    bitacora.info("Token recibido")

    # Bucle de consultas a la API
    limit = 50
    offset = 0
    total = None
    funcionarios_presentes_contador = 0
    funcionarios_insertados_contador = 0
    personas_omitidas_contador = 0
    while True:
        # Llamar a la API v1 personas
        bitacora.info("Consultando desde el registro %s", offset)
        response = requests.get(
            url=f"{base_url}/v1/personas",
            headers={"authorization": f"Bearer {token}"},
            params={"limit": limit, "offset": offset},
        )
        if response.status_code != 200:
            mensaje = f"Fallo la consulta de personas con error {response.status_code}"
            set_task_error(mensaje)
            bitacora.error(mensaje)
            return
        data = response.json()
        if total is None:
            total = data["total"]
            bitacora.info("Total: %d", total)
        # Comparar
        for persona_datos in data["items"]:
            curp = persona_datos["curp"]
            email = persona_datos["email"]
            if curp != "" and email != "" and email.endswith("@coahuila.gob.mx"):
                funcionario = Funcionario.query.filter(or_(Funcionario.curp == curp, Funcionario.email == email)).first()
                if funcionario is None:
                    funcionarios_insertados_contador += 1
                    Funcionario(
                        nombres=persona_datos["nombres"],
                        apellido_paterno=persona_datos["apellido_primero"],
                        apellido_materno=persona_datos["apellido_segundo"],
                        curp=curp,
                        email=email,
                    ).save()
                else:
                    funcionarios_presentes_contador += 1
            else:
                personas_omitidas_contador += 1
        # Saltar
        if offset + limit >= total:
            break
        offset += limit
    # Terminar
    bitacora.info("Se han insertado %s funcionarios", funcionarios_insertados_contador)
    bitacora.info("Hay %s personas ya presentes en funcionarios, se omiten", funcionarios_presentes_contador)
    bitacora.info("En %s personas no hay CURP o email coahuila.gob.mx", personas_omitidas_contador)
    set_task_progress(100)
    mensaje_final = "Terminado sincronizar satisfactoriamente"
    bitacora.info(mensaje_final)
    return
