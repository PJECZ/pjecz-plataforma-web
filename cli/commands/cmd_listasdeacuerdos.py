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
    """ Alimentar """
    # Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(DEPOSITO)
    # Bucle por las autoridades
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == 'A').all()
    for autoridad in autoridades_activas:
        subdirectorio = f'{DIRECTORIO}/{autoridad.distrito.nombre}/{autoridad.descripcion}'
        click.echo(subdirectorio)
        #for blob in bucket.list_blobs(prefix=subdirectorio):
        #    click.echo('  ' + blob.name)
    # Real 'Distrito de Monclova', mal 'Distrito Judicial de Monclova'
    subdirectorio = f'{DIRECTORIO}/Distrito de Monclova/Juzgado Primero de Primera Instancia en Materia Civil Monclova'
    for blob in bucket.list_blobs(prefix=subdirectorio):
        click.echo(f'  {blob.name}')


cli.add_command(alimentar)
