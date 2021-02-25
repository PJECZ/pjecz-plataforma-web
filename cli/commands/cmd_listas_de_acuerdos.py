"""
Listas de Acuerdos
"""
import click

from plataforma_web.blueprints.listas_de_acuerdos import tasks


@click.group()
def cli():
    """ Listas de Acuerdos """


@click.command()
@click.argument("autoridad_id", type=int)
def rastrear(autoridad_id):
    """ Rastrear las listas de acuerdos en Storage para agregarlas o actualizarlas a la BD """
    tasks.rastrear(autoridad_id)


cli.add_command(rastrear)
