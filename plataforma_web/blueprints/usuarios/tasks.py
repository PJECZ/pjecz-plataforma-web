"""
Usuarios, tareas para ejecutar en el fondo

- definir_oficinas: Definir las oficinas a partir de una relacion entre email y oficina
- enviar_reporte: Enviar via correo electronico el reporte de usuarios
- estandarizar: Estandarizar nombres, apellidos y puestos en mayusculas
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
import csv
import locale
import logging
import os
from pathlib import Path

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

USUARIOS_EMAILS_DISTRITOS_CSV = "seed/usuarios_emails_distritos.csv"

USUARIOS_OFICINAS_CSV = "seed/usuarios_oficinas.csv"


def definir_oficinas():
    """Definir las oficinas a partir de una relacion entre email y oficina"""

    # Iniciar
    bitacora.info("Inicia definir oficinas")

    # Tomar oficina NO DEFINIDO
    oficina_no_definido = Oficina.query.filter_by(clave="ND").first()
    if oficina_no_definido is None:
        mensaje = "No se encontró la oficina NO DEFINIDO"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Definir las equivalencias entre distrito_nombre y la oficina
    oficinas_relacion_distritos_nombres = {
        "ACUÑA": Oficina.query.filter_by(clave="DACU").first(),
        "MONCLOVA": Oficina.query.filter_by(clave="DMON").first(),
        "PARRAS": Oficina.query.filter_by(clave="DPAR").first(),
        "PIEDRAS NEGRAS": Oficina.query.filter_by(clave="DRGR").first(),
        "SABINAS": Oficina.query.filter_by(clave="DSAB").first(),
        "SALTILLO": Oficina.query.filter_by(clave="DSAL").first(),
        "SAN PEDRO": Oficina.query.filter_by(clave="DSPC").first(),
        "TORREON": Oficina.query.filter_by(clave="DTOR").first(),
    }
    for distrito_nombre, oficina in oficinas_relacion_distritos_nombres.items():
        if oficina is None:
            mensaje = "No se encontró la oficina para el distrito %s" % distrito_nombre
            set_task_error(mensaje)
            bitacora.error(mensaje)
            return

    # Cargar archivo CSV
    ruta = Path(USUARIOS_EMAILS_DISTRITOS_CSV)
    if not ruta.exists():
        mensaje = "No se encontró {ruta.name}"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return
    if not ruta.is_file():
        mensaje = "No es un archivo {ruta.name}"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return
    contador = 0
    usuarios_cambiados_contador = 0
    usuarios_sin_cambios_contador = 0
    emails_no_encontrados = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            email = row["email"].strip().lower()
            distrito_nombre = row["distrito"].strip().upper()
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario is None:
                emails_no_encontrados += 1
                bitacora.warning("No se encontró el email %s", email)
            else:
                if usuario.oficina == oficina_no_definido:
                    if distrito_nombre in oficinas_relacion_distritos_nombres:
                        usuario.oficina = oficinas_relacion_distritos_nombres[distrito_nombre]
                        usuario.save()
                        usuarios_cambiados_contador += 1
                else:
                    usuarios_sin_cambios_contador += 1
            contador += 1
            if contador % 100 == 0:
                bitacora.info("Procesados %d", contador)

        # Cargar archivo CSV usuarios oficinas
        oficina_relacion_email = Path(USUARIOS_OFICINAS_CSV)
        if not oficina_relacion_email.exists():
            mensaje = "No se encontró {oficina_relacion_email.name}"
            set_task_error(mensaje)
            bitacora.error(mensaje)
            return
        if not oficina_relacion_email.is_file():
            mensaje = "No es un archivo {oficina_relacion_email.name}"
            set_task_error(mensaje)
            bitacora.error(mensaje)
            return
        contador1 = 0
        usuarios_cambiados_contador1 = 0
        usuarios_sin_cambios_contador1 = 0
        emails_no_encontrados1 = 0
        with open(ruta, encoding="utf8") as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                clave_oficina = row["clave"]
                usuario_email = row["email"]
                # consultar el usuario que coincida con el email:
                # SELECT * FROM usuarios WHERE email = {usuario_email}
                usuario_c = Usuario.query.filter_by(email=usuario_email).first()
                # verifica si el usuario existe
                if usuario_c is None:
                    emails_no_encontrados1 += 1
                    bitacora.warning("Al asignar oficina id: No se encontró el email %s", usuario_email)
                else:
                    # verifica si el usuario YA tiene asignada una oficina
                    if usuario_c.oficina_id != 1:
                        usuarios_sin_cambios_contador1 += 1
                        bitacora.warning("Usuario {usuario_c.email} ya tiene asignada id oficina")
                    else:
                        # Si no tienen oficina, consultar mediante la clave:
                        # SELECT id FROM oficinas WHERE 'clave' = {clave_oficina}
                        usuario_c.oficina_id = Oficina.query.get().filter_by(clave=clave_oficina)
                        # Guardar los cambios
                        usuario_c.save()
                        # sumar al contador
                        usuarios_cambiados_contador1 += 1
                contador1 += 1
                if contador1 % 100 == 0:
                    bitacora.info("Usuarios asignados a una oficina %d", contador1)

    # Terminar
    set_task_progress(100)
    mensaje_final = f"Terminado definir oficinas satisfactoriamente con {contador} usuarios actualizados"
    bitacora.info(mensaje_final)
    return mensaje_final


def enviar_reporte():
    """Enviar reporte de usuarios via correo electronico"""

    # Iniciar
    bitacora.info("Inicia enviar reporte")

    # Consultar
    usuarios = Usuario.query.filter_by(estatus="A")
    bitacora.info("Hay %s usuarios activos", usuarios.count())

    # Terminar
    set_task_progress(100)
    mensaje_final = "Terminado enviar reporte satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final


def estandarizar():
    """Estandarizar nombres, apellidos y puestos en mayusculas"""

    # Iniciar
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
        if (
            nombres != usuario.nombres
            or apellido_paterno != usuario.apellido_paterno
            or apellido_materno != usuario.apellido_materno
            or puesto != usuario.puesto
        ):
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

    # Terminar
    bitacora.info("Se actualizaron %d usuarios", usuarios_actualizados_contador)
    bitacora.info("Se insertaron o actualizaron %d usuarios_roles", usuarios_roles_contador)
    set_task_progress(100)
    mensaje_final = f"Terminado estandarizar satisfactoriamente"
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
    # Terminar
    bitacora.info("Se han insertado %s usuarios", usuarios_insertados_contador)
    bitacora.info("Hay %s personas ya presentes, se omiten", usuarios_presentes_contador)
    bitacora.info("En %s personas no hay CURP o email coahuila.gob.mx", personas_omitidas_contador)
    set_task_progress(100)
    mensaje_final = "Terminado sincronizar satisfactoriamente"
    bitacora.info(mensaje_final)
    return
