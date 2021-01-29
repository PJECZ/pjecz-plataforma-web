"""
Alimentar listas de acuerdos
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

LISTAS_DE_ACUERDOS_CSV = 'seed/listas_de_acuerdos.csv'


def alimentar_listas_de_acuerdos():
    """ Alimentar Listas de Acuerdos """
    listas_de_acuerdos_csv = Path(LISTAS_DE_ACUERDOS_CSV)
    if listas_de_acuerdos_csv.exists():
        click.echo('Alimentando Listas de Acuerdos...')
        with open(listas_de_acuerdos_csv, encoding='utf8') as puntero:
            contador = 0
            rows = csv.DictReader(puntero)
            for row in rows:
                datos = {
                    'autoridad_id': int(row['autoridad_id']),
                    'archivo': row['archivo'].strip(),
                    'fecha': datetime.strptime(row['fecha'], '%Y-%m-%d'),
                    'descripcion': row['descripcion'].strip(),
                    'url': row['url'].strip(),
                }
                ListaDeAcuerdo(**datos).save()
                contador += 1
                if contador % 1000 == 0:
                    click.echo(f'  Van {contador} registros...')
    else:
        click.echo(f'ERROR: No se encontró {LISTAS_DE_ACUERDOS_CSV}')
