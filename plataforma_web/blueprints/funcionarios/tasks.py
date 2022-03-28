"""
Funcionarios, tareas para ejecutar en el fondo

- asignar_oficinas: Asignar funcionarios_oficinas a partir de una direccion
- limpiar_oficinas: Limpiar funcionarios_oficinas
- enviar_reporte: Enviar via correo electronico el reporte de funcionarios
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
from datetime import datetime
import locale
import logging
import os
import requests

from dotenv import load_dotenv
from sqlalchemy import or_

from lib.tasks import set_task_progress, set_task_error
from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.domicilios.models import Domicilio
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


def sincronizar():
    """Sincronizar funcionarios con la API de RRHH Personal"""

    # Iniciar
    bitacora.info("Inicia sincronizar")

    # Tomar variables del entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL")
    username = os.getenv("RRHH_PERSONAL_API_USERNAME")
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD")

    # Iniciar sesion
    try:
        response = requests.post(
            url=f"{base_url}/token",
            data={"username": username, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
    except ConnectionError as error:
        mensaje = f"No se pudo conectar con la API de RRHH Personal: {error}"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return
    if response.status_code != 200:
        mensaje = f"Fallo el inicio de sesion con error {response.status_code}"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return
    token = response.json()["access_token"]
    bitacora.info("Token recibido")

    # Bucle de consultas a la API
    limit = 10
    offset = 0
    total = None
    funcionarios_presentes_contador = 0
    funcionarios_insertados_contador = 0
    funcionarios_actualizados_contador = 0
    personas_omitidas_contador = 0
    while True:
        # Llamar a la API Personas
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
        personas_response = response.json()
        if total is None:
            total = personas_response["total"]
            bitacora.info("Total: %d", total)
        # Comparar
        for persona_data in personas_response["items"]:
            persona_id = persona_data["id"]
            nombres = (safe_string(persona_data["nombres"]),)
            apellido_paterno = (safe_string(persona_data["apellido_primero"]),)
            apellido_materno = (safe_string(persona_data["apellido_segundo"]),)
            curp = persona_data["curp"]
            email = persona_data["email"]
            if curp != "" and email != "" and email.endswith("@coahuila.gob.mx"):
                # Llamar a la API Historial de Puestos
                response = requests.get(
                    url=f"{base_url}/v1/historial_puestos",
                    headers={"authorization": f"Bearer {token}"},
                    params={"persona_id": persona_id, "limit": 1, "offset": 0},
                )
                if response.status_code != 200:
                    mensaje = f"Fallo la consulta de historial de puestos con error {response.status_code}"
                    set_task_error(mensaje)
                    bitacora.error(mensaje)
                    return
                historial_puestos_response = response.json()
                if historial_puestos_response["total"] == 0:
                    personas_omitidas_contador += 1
                    continue
                historial_puesto_data = historial_puestos_response["items"][0]  # Tomar el primero que debe ser el mas reciente
                puesto = historial_puesto_data["puesto_funcion_nombre"]
                # Consultar el Centro de Trabajo
                centro_trabajo_clave = historial_puesto_data["centro_trabajo"]
                centro_trabajo = CentroTrabajo.query.filter(CentroTrabajo.clave == centro_trabajo_clave).first()
                if centro_trabajo is None:
                    bitacora.error('No se encuentra el centro de trabajo "%s"', centro_trabajo_clave)
                    personas_omitidas_contador += 1
                    continue
                # Consultar funcionario
                funcionario = Funcionario.query.filter(or_(Funcionario.curp == curp, Funcionario.email == email)).first()
                if funcionario is None:
                    # Insertar funcionario
                    funcionarios_insertados_contador += 1
                    Funcionario(
                        centro_trabajo=centro_trabajo,
                        nombres=nombres,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        curp=curp,
                        email=email,
                        puesto=puesto,
                        ingreso_fecha=INGRESO_FECHA_POR_DEFECTO,
                    ).save()
                else:
                    # Actualizar funcionario
                    ha_cambiado = False
                    if funcionario.centro_trabajo != centro_trabajo:
                        funcionario.centro_trabajo = centro_trabajo
                        ha_cambiado = True
                    if funcionario.nombres != nombres:
                        funcionario.nombres = nombres
                        ha_cambiado = True
                    if funcionario.apellido_paterno != apellido_paterno:
                        funcionario.apellido_paterno = apellido_paterno
                        ha_cambiado = True
                    if funcionario.apellido_materno != apellido_materno:
                        funcionario.apellido_materno = apellido_materno
                        ha_cambiado = True
                    if funcionario.puesto != puesto:
                        funcionario.puesto = puesto
                        ha_cambiado = True
                    if funcionario.telefono != centro_trabajo.telefono:
                        funcionario.telefono = centro_trabajo.telefono
                        ha_cambiado = True
                    if ha_cambiado:
                        funcionario.save()
                        funcionarios_actualizados_contador += 1
                    else:
                        funcionarios_presentes_contador += 1
            else:
                personas_omitidas_contador += 1
        # Saltar
        if offset + limit >= total:
            bitacora.info("Se han procesado %d personas", offset + limit)
            break
        offset += limit
    # Terminar
    if funcionarios_insertados_contador > 0:
        bitacora.info("Se han insertado %s", funcionarios_insertados_contador)
    if funcionarios_actualizados_contador > 0:
        bitacora.info("Se han actualizado %s", funcionarios_actualizados_contador)
    if funcionarios_presentes_contador > 0:
        bitacora.info("Hay %s ya presentes que no se cambiaron", funcionarios_presentes_contador)
    if personas_omitidas_contador > 0:
        bitacora.info("Se omitieron %s porque les faltan datos", personas_omitidas_contador)
    set_task_progress(100)
    mensaje_final = "Terminado sincronizar satisfactoriamente"
    bitacora.info(mensaje_final)
    return
