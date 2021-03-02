"""
Tareas
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

app = create_app()
db.app = app


@click.group()
def cli():
    """ Tareas """


@click.command()
def terminar():
    """ Terminar todas las tareas """
    contador = 0
    for tarea in Tarea.query.filter(Tarea.ha_terminado == False).all():
        tarea.ha_terminado = True
        tarea.save()
        contador += 1
    click.echo(f"Se han cambiado {contador} tareas como terminadas.")


cli.add_command(terminar)
