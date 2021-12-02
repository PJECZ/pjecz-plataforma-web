"""
Alimentar materias
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.materias.models import Materia

MATERIAS_CSV = "seed/materias.csv"


def alimentar_materias():
    """Alimentar materias"""
    ruta = Path(MATERIAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando materias...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            materia_id = int(row["materia_id"])
            if materia_id != contador + 1:
                click.echo(f"  AVISO: materia_id {materia_id} no es consecutivo")
                continue
            Materia(
                nombre=safe_string(row["nombre"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} materias alimentadas.")
