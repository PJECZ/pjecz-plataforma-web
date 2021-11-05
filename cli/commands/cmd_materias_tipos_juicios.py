"""
Materias-Tipos Juicios

- respaldar: Respaldar a un archivo CSV
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.respaldar_materias_tipos_juicios import respaldar_materias_tipos_juicios

app = create_app()
db.app = app


@click.group()
def cli():
    """Materias-Tipos Juicios"""


@click.command()
@click.option("--output", default="materias_tipos_juicios.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_materias_tipos_juicios(output)


cli.add_command(respaldar)
