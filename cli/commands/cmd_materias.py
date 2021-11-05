"""
Materias

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_materias import respaldar_materias

app = create_app()
db.app = app


@click.group()
def cli():
    """Materias"""


@click.command()
@click.option("--output", default="materias.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_materias(output)


cli.add_command(respaldar)
