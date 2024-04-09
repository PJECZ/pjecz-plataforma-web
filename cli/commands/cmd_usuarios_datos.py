"""
Usuarios Datos

- exportar_xlsx: Exporta usuarios_datos a un archivo xlsx
"""

import sys

import click

from lib.exceptions import MyAnyError
from plataforma_web.blueprints.usuarios_datos.tasks import exportar_xlsx as task_exportar_xlsx


@click.group()
def cli():
    """Usuarios-Datos"""


@click.command()
def exportar_xlsx():
    """Exportar Personas a un archivo XLSX"""

    # Ejecutar la tarea
    try:
        mensaje_termino, _, _ = task_exportar_xlsx()
    except MyAnyError as error:
        click.echo(click.style(str(error), fg="red"))
        sys.exit(1)

    # Mensaje de termino
    click.echo(click.style(mensaje_termino, fg="green"))


cli.add_command(exportar_xlsx)
