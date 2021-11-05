"""
Roles-Permisos

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_roles_permisos import respaldar_roles_permisos

app = create_app()
db.app = app


@click.group()
def cli():
    """Roles - Permisos"""


@click.command()
@click.option("--output", default="roles_permisos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_roles_permisos(output)


cli.add_command(respaldar)
