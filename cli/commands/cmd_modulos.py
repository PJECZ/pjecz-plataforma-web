"""
Modulos

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_modulos import respaldar_modulos

app = create_app()
db.app = app


@click.group()
def cli():
    """Modulos"""


@click.command()
@click.option("--output", default="modulos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_modulos(output)


cli.add_command(respaldar)
