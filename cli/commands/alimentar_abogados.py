"""
Alimentar abogados
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.abogados.models import Abogado

ABOGADOS_CSV = 'seed/abogados.csv'


def alimentar_abogados():
    """ Alimentar abogados """
    abogados_csv = Path(ABOGADOS_CSV)
    if abogados_csv.exists():
        with open(abogados_csv) as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                try:
                    numero = int(row['numero'].strip())
                    fecha = datetime.strptime(row['fecha'].strip(), '%Y-%m-%d')
                except ValueError as mensaje:
                    click.echo(f'Dato con error: {mensaje}')
                datos = {
                    'numero': numero,
                    'nombre': row['nombre'].strip(),
                    'libro': row['libro'].strip(),
                    'fecha': fecha,
                }
                Abogado(**datos).save()
        click.echo('Abogados alimentados.')
    else:
        click.echo(f'ERROR: No se encontró {ABOGADOS_CSV}')
