"""
Usuarios, tareas para ejecutar en el fondo

- estandarizar: Estandarizar nombres, apellidos y puestos en mayusculas
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""

import locale
import logging
import os

import requests
from dotenv import load_dotenv
from sqlalchemy import or_

from lib.pwgen import generar_contrasena
from lib.safe_string import safe_string
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.extensions import pwd_context

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

TIMEOUT = 16


def estandarizar():
    """Estandarizar nombres, apellidos y puestos en mayusculas"""

    # Iniciar tarea
    mensaje_inicial = "Inicia estandarizar nombres, apellidos y puestos en mayusculas"
    set_task_progress(0, mensaje_inicial)
    bitacora.info("Inicia estandarizar")

    # Tomar rol SOPORTE USUARIO
    rol = Rol.query.filter_by(nombre="SOPORTE USUARIO").first()
    if rol is None:
        mensaje = "No se encontró el rol SOPORTE USUARIO"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Consultar y estandarizar
    contador = 0
    usuarios_actualizados_contador = 0
    usuarios_roles_contador = 0
    usuarios = Usuario.query.filter_by(estatus="A")
    for usuario in usuarios:
        # Estandarizar campos
        nombres = safe_string(usuario.nombres)
        apellido_paterno = safe_string(usuario.apellido_paterno)
        apellido_materno = safe_string(usuario.apellido_materno)
        puesto = safe_string(usuario.puesto)
        if puesto == "":
            puesto = "ND"
        if nombres != usuario.nombres or apellido_paterno != usuario.apellido_paterno or apellido_materno != usuario.apellido_materno or puesto != usuario.puesto:
            usuario.nombres = nombres
            usuario.apellido_paterno = apellido_paterno
            usuario.apellido_materno = apellido_materno
            usuario.puesto = puesto
            usuario.save()
            usuarios_actualizados_contador += 1
        # Saltar si el correo electronico no es coahuila.gob.mx
        if usuario.email.endswith("@coahuila.gob.mx"):
            continue
        # Que tenga el rol SOPORTE USUARIO
        if usuario.usuarios_roles is None:
            UsuarioRol(usuario=usuario, rol=rol, descripcion=f"{usuario.email} en {rol.nombre}").save()
            usuarios_roles_contador += 1
        else:
            tiene_ese_rol = False
            for usuario_rol in usuario.usuarios_roles:
                if usuario_rol.rol == rol:
                    tiene_ese_rol = True
                    if usuario_rol.rol.estatus != "A":
                        usuario_rol.rol.estatus = "A"
                        usuario_rol.rol.save()
                        usuarios_roles_contador += 1
            if not tiene_ese_rol:
                UsuarioRol(
                    usuario=usuario,
                    rol=rol,
                    descripcion=f"{usuario.email} en {rol.nombre}",
                ).save()
                usuarios_roles_contador += 1
        # Incrementar contador
        contador += 1
        if contador % 100 == 0:
            bitacora.info("Procesados %d", contador)

    # Terminar tarea
    mensaje_final = f"Se actualizaron {usuarios_actualizados_contador} usuarios, "
    mensaje_final += f"se insertaron o actualizaron {usuarios_roles_contador} usuarios_roles"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final


def sincronizar():
    """Sincronizar usuarios con la API de RRHH Personal"""

    # Iniciar tarea
    mensaje_inicial = "Inicia sincronizar usuarios con la API de RRHH Personal"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

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

    # Definir rol SOPORTE USUARIO
    rol_soporte_usuario = Rol.query.filter_by(nombre="SOPORTE USUARIO").first()
    if rol_soporte_usuario is None:
        mensaje = "No se encontró el rol SOPORTE USUARIO"
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
        timeout=TIMEOUT,
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
            timeout=TIMEOUT,
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
                    usuario = Usuario(
                        autoridad=autoridad_no_definido,
                        oficina=oficina_no_definido,
                        email=email,
                        nombres=persona_datos["nombres"],
                        apellido_paterno=persona_datos["apellido_primero"],
                        apellido_materno=persona_datos["apellido_segundo"],
                        curp=curp,
                        puesto="ND",
                        telefono_celular="ND",
                        workspace="COAHUILA",
                        contrasena=pwd_context.hash(generar_contrasena()),
                    ).save()
                    UsuarioRol(
                        rol=rol_soporte_usuario,
                        usuario=usuario,
                        descripcion=f"{usuario.email} en {rol_soporte_usuario.nombre}",
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

    # Terminar tarea
    mensaje_final = f"Se han insertado {usuarios_insertados_contador} usuarios, "
    mensaje_final += f"hay {usuarios_presentes_contador} personas ya presentes, se omiten, "
    mensaje_final += f"en {personas_omitidas_contador} personas no hay CURP o email coahuila.gob.mx"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return
