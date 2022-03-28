"""
Centros de Trabajo, tareas para ejecutar en el fondo

- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
import logging
import os
import requests

from dotenv import load_dotenv

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.distritos.models import Distrito

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("centros_trabajos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app


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

    # Obtener el distrito NO DEFINIDO
    distrito_no_definido = Distrito.query.filter(Distrito.nombre == "NO DEFINIDO").first()
    if distrito_no_definido is None:
        mensaje = "No se encuentra el distrito NO DEFINIDO"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Bucle de consultas a la API
    limit = 50
    offset = 0
    total = None
    centros_trabajos_presentes_contador = 0
    centros_trabajos_insertados_contador = 0
    centros_trabajos_omitidas_contador = 0
    while True:
        # Llamar a la API v1 centros_trabajos
        bitacora.info("Consultando desde el registro %s", offset)
        response = requests.get(
            url=f"{base_url}/v1/centros_trabajos",
            headers={"authorization": f"Bearer {token}"},
            params={"limit": limit, "offset": offset},
        )
        if response.status_code != 200:
            mensaje = f"Fallo la consulta de centros de trabajo con error {response.status_code}"
            set_task_error(mensaje)
            bitacora.error(mensaje)
            return
        data = response.json()
        if total is None:
            total = data["total"]
            bitacora.info("Total: %d", total)
        # Comparar
        for centro_trabajo_datos in data["items"]:
            clave = centro_trabajo_datos["clave"]
            if clave != "":
                funcionario = CentroTrabajo.query.filter(CentroTrabajo.clave == clave).first()
                if funcionario is None:
                    centros_trabajos_insertados_contador += 1
                    CentroTrabajo(
                        clave=clave,
                        nombre=centro_trabajo_datos["nombre"],
                        area=centro_trabajo_datos["area"],
                        distrito=distrito_no_definido,
                    ).save()
                else:
                    centros_trabajos_presentes_contador += 1
            else:
                centros_trabajos_omitidas_contador += 1
        # Saltar
        if offset + limit >= total:
            break
        offset += limit
    # Terminar
    if centros_trabajos_insertados_contador > 0:
        bitacora.info("Se han insertado %s", centros_trabajos_insertados_contador)
    if centros_trabajos_presentes_contador > 0:
        bitacora.info("Hay %s ya presentes", centros_trabajos_presentes_contador)
    if centros_trabajos_omitidas_contador > 0:
        bitacora.info("Se omitieron %s porque les faltan datos", centros_trabajos_omitidas_contador)
    set_task_progress(100)
    mensaje_final = "Terminado sincronizar satisfactoriamente"
    bitacora.info(mensaje_final)
    return
