"""
Inventarios Custodias

- actualizar: Actualizar las cantidades de equipos y fotos de las custodias
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """Inventarios Custodias"""


@click.command()
def actualizar():
    """Actualizar las cantidades de equipos y fotos de las custodias"""
    # Poner tarea en el fondo
    app.task_queue.enqueue("plataforma_web.blueprints.inv_custodias.tasks.actualizar")
    click.echo("Asignar oficinas se está ejecutando en el fondo.")


cli.add_command(actualizar)
