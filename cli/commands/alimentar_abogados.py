"""
Alimentar abogados
"""
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
                datos = {
                    'numero': int(row['nuemro'].strip()),
                    'nombre': row['nombres'].strip(),
                    'libro': row['libro'].strip(),
                    'fecha': row['fecha'].strip(),
                }
                Abogado(**datos).save()
        click.echo('Abogados alimentados.')
    else:
        click.echo(f'ERROR: No se encontró {ABOGADOS_CSV}')
