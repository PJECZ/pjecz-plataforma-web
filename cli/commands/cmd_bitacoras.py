"""
Bitacoras
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """Bitacoras"""


@click.command()
def enviar():
    """Enviar mensaje"""
    app.task_queue.enqueue(
        "plataforma_web.blueprints.bitacoras.tasks.enviar",
        usuario_id=None,
    )
    click.echo("Enviar bitácora se está ejecutando en el fondo.")


cli.add_command(enviar)
