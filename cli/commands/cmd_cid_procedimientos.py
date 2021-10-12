"""
CID Procedimientos

- crear_pdf: Crear PDF
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """CID Procedimientos"""


@click.command()
@click.argument("cid_procedimiento_id", type=int)
def crear_pdf(cid_procedimiento_id):
    """Crear PDF"""
    app.task_queue.enqueue(
        "plataforma_web.blueprints.cid_procedimientos.tasks.crear_pdf",
        cid_procedimiento_id=cid_procedimiento_id,
    )
    click.echo("Crear PDF se está ejecutando en el fondo.")


cli.add_command(crear_pdf)
