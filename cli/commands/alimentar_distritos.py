"""
Alimentar distritos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito

DISTRITOS_CSV = "seed/distritos_autoridades_usuarios.csv"


def alimentar_distritos():
    """ Alimentar distritos """
    distritos_cvs = Path(DISTRITOS_CSV)
    if not distritos_cvs.exists():
        click.echo(f"  No se alimentaron distritos porque no encontró {DISTRITOS_CSV}")
        return
    agregados = []
    with open(distritos_cvs, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            nombre = row["distrito"].strip()
            es_distrito_judicial = int(row["es_distrito_judicial"].strip()) == 1
            if nombre in agregados:
                continue
            Distrito(nombre=nombre, es_distrito_judicial=es_distrito_judicial).save()
            agregados.append(nombre)
    click.echo(f"- {len(agregados)} distritos alimentados.")
