"""
Alimentar autoridades
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad

AUTORIDADES_CSV = "seed/distritos_autoridades.csv"


def alimentar_autoridades():
    """ Alimentar autoridades """
    autoridades_csv = Path(AUTORIDADES_CSV)
    if not autoridades_csv.exists():
        click.echo(f"- NO se alimentaron autoridades porque no se encontró {AUTORIDADES_CSV}")
        return
    contador = 0
    with open(autoridades_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            datos = {
                "descripcion": row["autoridad"].strip(),
                "distrito": Distrito.query.filter_by(nombre=row["distrito"].strip()).first(),
                "email": row["email"].strip(),
                "directorio_listas_de_acuerdos": row["directorio_listas_de_acuerdos"].strip(),
                "directorio_sentencias": row["directorio_sentencias"].strip(),
            }
            Autoridad(**datos).save()
            contador += 1
    click.echo(f"- {contador} autoridades alimentadas.")
