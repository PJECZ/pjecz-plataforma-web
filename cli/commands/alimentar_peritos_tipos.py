"""
Alimentar peritos tipos
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo

PERITOS_TIPOS_CSV = "seed/peritos_tipos.csv"


def alimentar_peritos_tipos():
    """Alimentar tipos de peritos"""
    ruta = Path(PERITOS_TIPOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando tipos de peritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            perito_tipo_id = int(row["perito_tipo_id"])
            if perito_tipo_id != contador + 1:
                click.echo(f"  AVISO: perito_tipo_id {perito_tipo_id} no es consecutivo")
                continue
            PeritoTipo(
                nombre=safe_string(row["nombre"], save_enie=True),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} tipos de peritos alimentados.")
