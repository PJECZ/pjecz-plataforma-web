"""
Listas de Acuerdos
"""
import click

from plataforma_web.app import create_app

app = create_app()


@click.group()
def cli():
    """ Listas de Acuerdos """


@click.command()
@click.argument("autoridad_id", type=int)
def rastrear(autoridad_id):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    app.task_queue.enqueue("plataforma_web.blueprints.listas_de_acuerdos.tasks.rastrear", usuario_id=None, autoridad_id=autoridad_id)
    click.echo("Rastrear las listas de acuerdo se está ejecutando en el fondo.")


cli.add_command(rastrear)
