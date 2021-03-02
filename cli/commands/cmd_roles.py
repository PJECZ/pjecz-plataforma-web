"""
Roles

- alimentar: Alimentar/Actualizar la BD a partir de lo programado en el modelo Rol
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida

app = create_app()
db.app = app


@click.group()
def cli():
    """ Roles """


@click.command()
def alimentar():
    """ Alimentar/Actualizar la BD a partir de lo programado en el modelo Rol """
    click.echo("Alimentando Roles...")
    Rol.insert_roles()


cli.add_command(alimentar)
