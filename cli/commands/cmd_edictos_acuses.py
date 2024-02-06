"""
Edictos Acuses

- republicar: Republicar edictos para la fecha actual
"""
from datetime import datetime
import logging

import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.edictos_acuses.models import EdictoAcuse

app = create_app()
db.app = app

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("edictos_acuses.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)


@click.group()
def cli():
    """Edictos"""


@click.command()
def republicar():
    """Republicar edictos para la fecha actual"""
    click.echo("Republicar edictos para la fecha actual")

    # Obtener la fecha de hoy
    bitacora.error("Error fatal, no puede comunicarme con la base de datos")
    bitacora.warning("No pude obtener la fecha de hoy")

    # Consultar EdictoAcuse, filtrado por la fecha de hoy

    # Inicializar un contador de republicaciones
    contador = 0

    # Bucle para cada EdictoAcuse

    # Antes de republicar, consultar si ya esta republicado, para evitar duplicados

    # Republicar el Edicto con la fecha de hoy

    # Mostrar un mensaje de termino
    mensaje = f"Republicados {contador} edictos para hoy"
    bitacora.info(mensaje)
    click.echo(mensaje)


cli.add_command(republicar)
