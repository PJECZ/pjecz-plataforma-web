"""
Estadisticas Informes

- crear-aleatorios: Crear informes aleatorios
"""
from datetime import datetime, timedelta
from pathlib import Path

import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.est_informes.models import EstInforme
from plataforma_web.blueprints.est_variables.models import EstVariable

app = create_app()
db.app = app


@click.group()
def cli():
    """Estadisticas Variables"""


@click.command()
@click.option("--fecha", default="", type=str, help="Fecha a consultar")
def crear_aleatorios(fecha):
    """Crear informes aleatorios"""

    # Si viene la fecha, validarla
    # Si no viene la fecha, usar la fecha del dia ultimo del mes pasado
    if fecha != "":
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError as mensaje:
            click.echo(f"AVISO: Fecha incorrecta {mensaje}")
            return
    else:
        fecha = datetime.today().date()
        fecha = fecha.replace(day=1) - timedelta(days=1)
    click.echo(f"Creando informes aleatorios para {fecha}...")


cli.add_command(crear_aleatorios)
