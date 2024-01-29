"""
Edictos Acuses

- republicar: Republicar edictos para la fecha actual
"""
from datetime import datetime

import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.edictos.models import Edicto

app = create_app()
db.app = app


@click.group()
def cli():
    """Edictos"""


@click.command()
def republicar():
    """Republicar edictos para la fecha actual"""
    click.echo("Republicar edictos para la fecha actual")


cli.add_command(republicar)
