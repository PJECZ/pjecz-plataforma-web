"""
Distritos

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_distritos import respaldar_distritos

app = create_app()
db.app = app


@click.group()
def cli():
    """Distritos"""


@click.command()
@click.option("--output", default="distritos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_distritos(output)


cli.add_command(respaldar)
