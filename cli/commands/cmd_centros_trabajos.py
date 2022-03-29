"""
Centros de Trabajo

- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """Funcionarios"""


@click.command()
def sincronizar():
    """Sincronizar con RRHH Personal"""
    app.task_queue.enqueue("plataforma_web.blueprints.centros_trabajos.tasks.sincronizar")
    click.echo("Sincronizar se está ejecutando en el fondo.")


cli.add_command(sincronizar)
