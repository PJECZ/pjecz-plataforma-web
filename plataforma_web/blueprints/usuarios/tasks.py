"""
Usuarios, tareas para ejecutar en el fondo

- enviar_reporte: Enviar via correo electronico el reporte de usuarios
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

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("usuarios.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app

locale.setlocale(locale.LC_TIME, "es_MX.utf8")


def enviar_reporte():
    """Enviar reporte de usuarios via correo electronico"""

    # Iniciar
    bitacora.info("Inicia enviar reporte")

    # Consultar
    usuarios = db.session.query(Usuario).filter_by(estatus="A")
    bitacora.info("Total: %s", usuarios.count())

    # Terminar
    set_task_progress(100)
    mensaje_final = "Terminado enviar reporte satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final


def sincronizar():
    """Sincronizar usuarios con la API de RRHH Personal"""

    # Iniciar
    bitacora.info("Inicia sincronizar")

    # Definir la autoridad NO DEFINIDO
    autoridad_no_definido = Autoridad.query.filter_by(clave="ND").first()
    if autoridad_no_definido is None:
        mensaje = "No se encontró la autoridad NO DEFINIDO"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Definir la oficina NO DEFINIDO
    oficina_no_definido = Oficina.query.filter_by(clave="ND").first()
    if oficina_no_definido is None:
        mensaje = "No se encontró la oficina NO DEFINIDO"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

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
    usuarios_presentes_contador = 0
    usuarios_insertados_contador = 0
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
                usuario = Usuario.query.filter(or_(Usuario.curp == curp, Usuario.email == email)).first()
                if usuario is None:
                    Usuario(
                        autoridad=autoridad_no_definido,
                        oficina=oficina_no_definido,
                        nombres=persona_datos["nombres"],
                        apellido_paterno=persona_datos["apellido_primero"],
                        apellido_materno=persona_datos["apellido_segundo"],
                        curp=curp,
                        email=email,
                        contrasena="",
                    ).save()
                    usuarios_insertados_contador += 1
                else:
                    usuarios_presentes_contador += 1
            else:
                personas_omitidas_contador += 1
        # Saltar
        if offset + limit >= total:
            break
        offset += limit
    # Terminar
    bitacora.info("Se han insertado %s funcionarios", usuarios_insertados_contador)
    bitacora.info("Hay %s personas ya presentes en funcionarios, se omiten", usuarios_presentes_contador)
    bitacora.info("En %s personas no hay CURP o email coahuila.gob.mx", personas_omitidas_contador)
    set_task_progress(100)
    mensaje_final = "Terminado sincronizar satisfactoriamente"
    bitacora.info(mensaje_final)
    return
