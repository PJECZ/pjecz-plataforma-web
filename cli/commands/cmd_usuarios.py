"""
Usuarios

- estandarizar: Estandarizar nombres, apellidos y puestos en mayusculas
- nueva_api_key: Nueva API Key
- nueva_contrasena: Nueva contraseña
- sincronizar: Sincronizar con la API de RRHH Personal
"""
from datetime import datetime, timedelta

import click

from lib.pwgen import generar_api_key

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

app = create_app()
db.app = app


@click.group()
def cli():
    """Usuarios"""


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


cli.add_command(estandarizar)
cli.add_command(nueva_api_key)
cli.add_command(nueva_contrasena)
cli.add_command(sincronizar)
