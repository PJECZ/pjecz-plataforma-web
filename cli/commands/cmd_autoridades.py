"""
Autoridades

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_autoridades import respaldar_autoridades

app = create_app()
db.app = app


@click.group()
def cli():
    """Autoridades"""


@click.command()
@click.option("--output", default="autoridades.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_autoridades(output)


cli.add_command(respaldar)
