"""
Alimentar autoridades
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad

AUTORIDADES_CSV = 'seed/autoridades.csv'


def alimentar_autoridades():
    """ Alimentar autoridades """
    autoridades_csv = Path(AUTORIDADES_CSV)
    if autoridades_csv.exists():
        with open(autoridades_csv, encoding="utf8") as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                datos = {
                    'descripcion': row['descripcion'].strip(),
                    'distrito': Distrito.query.filter_by(nombre=row['distrito'].strip()).first(),
                    'email': row['email'].strip(),
                }
                Autoridad(**datos).save()
        click.echo('Autoridades alimentadas.')
    else:
        click.echo(f'ERROR: No se encontró {AUTORIDADES_CSV}')
