"""
Usuarios

- alimentar-notarias: Insertar notarias a partir de un archivo CSV
- estandarizar: Estandarizar nombres, apellidos y puestos en mayusculas
- nueva_api_key: Nueva API Key
- nueva_contrasena: Nueva contraseña
- sincronizar: Sincronizar con la API de RRHH Personal
"""
from datetime import datetime, timedelta
from pathlib import Path

import csv
import click

from lib.pwgen import generar_api_key, generar_contrasena
from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol
from plataforma_web.extensions import pwd_context

app = create_app()
db.app = app


@click.group()
def cli():
    """Usuarios"""


@click.command()
@click.argument("entrada_csv", type=str)
def alimentar_notarias(entrada_csv):
    """Insertar notarias a usuarios a partir de un archivo CSV"""
    # Validar que exista el archivo CSV
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return

    click.echo("Alimentando usuarios...")

    # Leer archivo CSV
    contador = 0
    with open(ruta, encoding="UTF8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:

            # Validar autoridad
            if "autoridad_id" in row:
                autoridad_id = row["autoridad_id"]
                autoridad = Autoridad.query.get(autoridad_id)
                if autoridad is None:
                    click.echo(f" AVISO: Falta la autoridad_id {autoridad_id}")
                    continue
            else:
                raise Exception(" ERROR: No tiene la columna autoridad_clave o autoridad_id")

            # Validar oficina
            if "oficina_id" in row:
                oficina_id = row["oficina_id"]
                oficina = Oficina.query.get(oficina_id)
                if oficina is None:
                    click.echo(f" AVISO: Falta la oficina_id {oficina_id}")
                    continue
            else:
                oficina = Oficina.query.get(1)  # Oficina NO DEFINIDO

            # Validar si existe email en la base de datos, se omite
            email = row["email"]
            if Usuario.query.filter_by(email=email).first() is not None:
                click.echo(f"AVISO: Ya existe un email registrado {email} en la base de datos, se omite")
                continue

            # Validar campos
            nombre = safe_string(row["nombre"])
            apellido_primero = safe_string(row["apellido_primero"])
            puesto = safe_string(row["puesto"])
            workspace = safe_string(row["workspace"])
            roles = row["roles"]

            # Insertar usuario
            usuario = Usuario(
                autoridad_id=autoridad_id,
                oficina_id=oficina_id,
                nombres=nombre,
                apellido_paterno=apellido_primero,
                email=email,
                puesto=puesto,
                workspace=workspace,
                contrasena=pwd_context.hash(generar_contrasena()),
                api_key="",
                api_key_expiracion=datetime(year=2000, month=1, day=1),
            )
            usuario.save()

            # Agregar Rol al usuario
            roles = Rol.query.filter_by(nombre=roles).first()
            if roles is None:
                click.echo(f"  AVISO: Falta el rol {roles}")
                continue
            UsuarioRol(
                usuario=usuario,
                rol=roles,
                descripcion=f"{usuario.email} en {roles.nombre}",
            ).save()

            # Contador de usuarios insertados
            contador += 1
            if contador % 50 == 0:
                click.echo(f" Van {contador}...")

    # Mensaje final
    click.echo(f"Se insertaron {contador} usuarios")


@click.command()
def estandarizar():
    """Estandarizar nombres, apellidos y puestos en mayusculas"""
    app.task_queue.enqueue("plataforma_web.blueprints.usuarios.tasks.estandarizar")
    click.echo("Estandarizar se está ejecutando en el fondo.")


@click.command()
@click.argument("email", type=str)
@click.option("--dias", default=90, help="Cantidad de días para expirar la API Key")
def nueva_api_key(email, dias):
    """Nueva API key"""
    usuario = Usuario.find_by_identity(email)
    if usuario is None:
        click.echo(f"No existe el e-mail {email} en usuarios")
        return
    api_key = generar_api_key(usuario.id, usuario.email)
    api_key_expiracion = datetime.now() + timedelta(days=dias)
    usuario.api_key = api_key
    usuario.api_key_expiracion = api_key_expiracion
    usuario.save()
    click.echo(f"Nueva API key para {usuario.email} es {api_key} que expira el {api_key_expiracion.strftime('%Y-%m-%d')}")


@click.command()
@click.argument("email", type=str)
def nueva_contrasena(email):
    """Nueva contraseña"""
    usuario = Usuario.find_by_identity(email)
    if usuario is None:
        click.echo(f"No existe el e-mail {email} en usuarios")
        return
    contrasena_1 = input("Contraseña: ")
    contrasena_2 = input("De nuevo la misma contraseña: ")
    if contrasena_1 != contrasena_2:
        click.echo("No son iguales las contraseñas. Por favor intente de nuevo.")
        return
    usuario.contrasena = pwd_context.hash(contrasena_1.strip())
    usuario.save()
    click.echo(f"Se ha cambiado la contraseña de {email} en usuarios")


@click.command()
def sincronizar():
    """Sincronizar con la API de RRHH Personal"""
    app.task_queue.enqueue("plataforma_web.blueprints.usuarios.tasks.sincronizar")
    click.echo("Sincronizar se está ejecutando en el fondo.")


cli.add_command(alimentar_notarias)
cli.add_command(estandarizar)
cli.add_command(nueva_api_key)
cli.add_command(nueva_contrasena)
cli.add_command(sincronizar)
