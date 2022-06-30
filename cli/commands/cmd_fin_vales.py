"""
Financieros Vales

- solicitar
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.fin_vales.models import FinVale

app = create_app()
db.app = app


@click.group()
def cli():
    """Financieros Vales"""


@click.command()
@click.argument("fin_vale_id")
@click.argument("contrasena")
def solicitar(fin_vale_id, contrasena):
    """Solicitar un vale"""

    # Validar vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        click.echo("No se encontró el vale")
        return
    if fin_vale.estatus != "A":
        click.echo("El vale esta eliminado")
        return
    click.echo(f'Voy a firmar el vale "{fin_vale.justificacion}"')

    # Poner tarea en el fondo
    app.task_queue.enqueue(
        "plataforma_web.blueprints.fin_vales.tasks.solicitar",
        fin_vale_id=fin_vale_id,
        contrasena=contrasena,
    )
    click.echo("Asignar oficinas se está ejecutando en el fondo.")


cli.add_command(solicitar)
