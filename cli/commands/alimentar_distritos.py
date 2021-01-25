"""
Alimentar distritos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito

DISTRITOS_CSV = 'seed/distritos.csv'


def alimentar_distritos():
    """ Alimentar distritos """
    distritos_cvs = Path(DISTRITOS_CSV)
    if distritos_cvs.exists():
        with open(distritos_cvs, encoding='utf8') as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                datos = {
                    'nombre': row['nombre'].strip(),
                }
                Distrito(**datos).save()
        click.echo('Distritos alimentados.')
    else:
        click.echo(f'ERROR: No se encontró {DISTRITOS_CSV}')
