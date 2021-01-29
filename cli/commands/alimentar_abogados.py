"""
Alimentar abogados
"""
from datetime import datetime
from pathlib import Path
import csv
from unidecode import unidecode
import click

from plataforma_web.blueprints.abogados.models import Abogado

ABOGADOS_CSV = 'seed/abogados.csv'


def alimentar_abogados():
    """ Alimentar abogados """
    abogados_csv = Path(ABOGADOS_CSV)
    if abogados_csv.exists():
        click.echo('Alimentando Abogados...')
        with open(abogados_csv, encoding='utf8') as puntero:
            contador = 0
            rows = csv.DictReader(puntero)
            for row in rows:
                try:
                    numero = int(row['numero'].strip())
                    nombre = unidecode(row['nombre'].strip()).upper()
                    fecha = datetime.strptime(row['fecha'].strip(), '%Y-%m-%d')
                    datos = {
                        'numero': numero,
                        'nombre': nombre,
                        'libro': row['libro'].strip(),
                        'fecha': fecha,
                    }
                    Abogado(**datos).save()
                    contador += 1
                    if contador % 1000 == 0:
                        click.echo(f'  Van {contador} registros...')
                except ValueError as mensaje:
                    click.echo(f'  Dato con error: {mensaje}')
    else:
        click.echo(f'ERROR: No se encontró {ABOGADOS_CSV}')
