"""
Listas de Acuerdos

- agregar_con_correo_electronico: Agregar una lista de acuerdos que se recibió vía correo electrónico
- rastrear: Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """ Listas de Acuerdos """


@click.command()
@click.argument("autoridad_email", type=str)
@click.argument("fecha", type=str)
@click.argument("archivo", type=str)
@click.option("--descripcion", default="", type=str)
@click.option("--url", default="", type=str)
def agregar(autoridad_email, fecha, archivo, descripcion=None, url=None):
    """ Agregar una lista de acuerdos que se recibió vía correo electrónico """
    resultado = app.task_queue.enqueue(
        "plataforma_web.blueprints.listas_de_acuerdos.tasks.agregar",
        usuario_id=None,
        autoridad_email=autoridad_email,
        fecha=fecha,
        archivo=archivo,
        descripcion=descripcion,
        url=url,
    )
    click.echo(f"Se ha lanzado la tarea en el fondo {resultado}")


@click.command()
@click.argument("autoridad_email", type=str)
def rastrear(autoridad_email):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    app.task_queue.enqueue(
        "plataforma_web.blueprints.listas_de_acuerdos.tasks.rastrear",
        usuario_id=None,
        autoridad_email=autoridad_email,
    )
    click.echo("Rastrear las listas de acuerdo se está ejecutando en el fondo.")


cli.add_command(agregar)
cli.add_command(rastrear)
