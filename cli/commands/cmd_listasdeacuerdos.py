"""
Listas de Acuerdos
"""
#from pathlib import Path
#import csv
import click
#from google.cloud import storage

from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.glosas.models import Glosa
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

DEPOSITO = 'pjecz-consultas'
DIRECTORIO = 'Listas de Acuerdos'
app = create_app()


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def alimentar():
    """ Alimentar """
    #client = storage.Client()
    #bucket = client.get_bucket(DEPOSITO)
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == 'A').all()
    #for autoridad in autoridades_activas:
    #    click.echo(f'{DIRECTORIO}/{autoridad.distrito.nombre}/{autoridad.descripcion}')


cli.add_command(alimentar)
