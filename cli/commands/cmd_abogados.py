"""
Abogados

- respaldar: Respaldar la tabla 'abogados' a su archivo CSV
- publicar: Publicar el archivo JSON en Storage para que el sitio web lo use con DataTables
"""
from datetime import datetime
from pathlib import Path
import json
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.abogados.models import Abogado
from plataforma_web.blueprints.distritos.models import Distrito

ABOGADOS_CSV = 'seed/abogados.csv'
ABOGADOS_JSON = 'json/abogados.json'

app = create_app()
db.app = app


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
@click.option('--desde', default='', type=str, help='Fecha de inicio, use AAAA-MM-DD')
def respaldar(desde):
    """ Respaldar la tabla abogados a su archivo CSV """
    try:
        if desde != '':
            desde_fecha = datetime.strptime(desde, '%Y-%m-%d')
        else:
            desde_fecha = None
    except ValueError:
        click.echo('Fecha desde es incorrecta.')
        return
    click.echo('Respaldando...')
    contador = 0
    if desde_fecha is None:
        abogados = Abogado.query.\
            filter(Abogado.estatus == 'A').\
            order_by(Abogado.fecha).\
            all()
    else:
        abogados = Abogado.query.\
            filter(Abogado.estatus == 'A').\
            filter(Abogado.fecha >= desde_fecha).\
            order_by(Abogado.fecha).\
            all()
    with open(ABOGADOS_CSV, 'w') as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(['numero', 'nombre', 'libro', 'fecha'])
        for abogado in abogados:
            escritor.writerow([
                abogado.numero,
                abogado.nombre,
                abogado.libro,
                abogado.fecha.strftime('%Y-%m-%d'),
            ])
            contador += 1
            if contador % 1000 == 0:
                click.echo(f'  Van {contador} registros...')
    click.echo(f'Respaldados {contador} registros en {ABOGADOS_CSV}')


@click.command()
def publicar():
    """ Publicar el archivo JSON en Storage para que el sitio web lo use con DataTables """
    ruta = Path(ABOGADOS_JSON)
    if not ruta.parent.exists():
        ruta.parent.mkdir(parents=True)
    abogados = Abogado.query.\
        filter(Abogado.estatus == 'A').\
        order_by(Abogado.fecha).\
        all()
    click.echo('Publicando...')
    registros = []
    for abogado in abogados:
        registros.append({
            'fecha': abogado.fecha.strftime('%Y-%m-%d'),
            'numero': abogado.numero,
            'libro': abogado.libro,
            'nombre': abogado.nombre,
        })
    datos = {'data': registros}
    with open(ruta, 'w') as puntero:
        puntero.write(json.dumps(datos))


cli.add_command(respaldar)
cli.add_command(publicar)
