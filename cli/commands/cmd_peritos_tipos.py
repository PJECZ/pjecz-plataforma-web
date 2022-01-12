"""
Peritos Tipos

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
import click

from cli.commands.alimentar_peritos_tipos import alimentar_peritos_tipos
from cli.commands.respaldar_peritos_tipos import respaldar_peritos_tipos

@click.group()
def cli():
    """Peritos Tipos"""


@click.command()
@click.argument()
def alimentar():
    """Alimentar a partir de un archivo CSV"""
    alimentar_peritos_tipos()


@click.command()
@click.option("--output", default="seed/peritos-tipos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_peritos_tipos(output)
