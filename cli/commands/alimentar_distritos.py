"""
Alimentar distritos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito

DISTRITOS_CSV = "seed/distritos.csv"


def alimentar_distritos():
    """Alimentar distritos"""
    ruta = Path(DISTRITOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando distritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Distrito(
                nombre=row["nombre"],
                nombre_corto=row["nombre_corto"],
                es_distrito_judicial=(row["es_distrito_judicial"] == "1"),
                estatus=row["estatus"],
            ).save()
            contador += 1
    click.echo(f"  {contador} distritos alimentados.")
