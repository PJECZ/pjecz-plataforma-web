"""
Usuarios

- alimentar: Alimentar insertando registros desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
- nueva_contrasena: Cambiar contraseña de un usuario
"""
import click

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
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar la tabla autoridades insertando registros desde un archivo CSV"""


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar la tabla autoridades a su archivo CSV"""


@click.command()
@click.argument("email", type=str)
def nueva_contrasena(email):
    """Cambiar contraseña de un usuario"""
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


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(nueva_contrasena)
