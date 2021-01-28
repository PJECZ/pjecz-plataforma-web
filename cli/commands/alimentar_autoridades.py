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
        click.echo('Alimentando Autoridades...')
        with open(autoridades_csv, encoding='utf8') as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                datos = {
                    'distrito': Distrito.query.filter_by(nombre=row['distrito'].strip()).first(),
                    'descripcion': row['descripcion'].strip(),
                    'email': row['email'].strip(),
                    'directorio_listas_de_acuerdos': row['directorio_listas_de_acuerdos'].strip(),
                    'directorio_sentencias': row['directorio_sentencias'].strip(),
                }
                Autoridad(**datos).save()
    else:
        click.echo(f'ERROR: No se encontró {AUTORIDADES_CSV}')
