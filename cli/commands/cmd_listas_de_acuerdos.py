"""
Listas de Acuerdos
"""
#from pathlib import Path
#import csv
import click
from google.cloud import storage

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.glosas.models import Glosa
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.peritos.models import Perito

app = create_app()
db.app = app

DEPOSITO = 'pjecz-consultas'
DIRECTORIO = 'Listas de Acuerdos'


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def alimentar():
    """ Alimentar la tabla a partir de los archivos en Storage """
    # Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(DEPOSITO)
    # Bucle por las autoridades
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == 'A').all()
    for autoridad in autoridades_activas:
        if autoridad.directorio_listas_de_acuerdos != '':
            subdirectorio = f'{DIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}'
            click.echo(subdirectorio)
            blobs = bucket.list_blobs(prefix=subdirectorio)
            if len(blobs) == 0:
                click.echo('! ' + blob.name)
            for blob in blobs:
                click.echo('  ' + blob.name)
                break


@click.command()
def respaldar():
    """ Respaldar la tabla a su archivo seed/listas_de_acuerdos.csv """
    click.echo('Pendiente programar.')


@click.command()
def actualizar():
    """ Actualizar listado JSON y subirlo a Storage """
    click.echo('Pendiente programar.')


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(actualizar)
