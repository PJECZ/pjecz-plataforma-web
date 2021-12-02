"""
Alimentar modulos
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.modulos.models import Modulo

MODULOS_CSV = "seed/modulos.csv"


def alimentar_modulos():
    """Alimentar modulos"""
    ruta = Path(MODULOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando módulos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Modulo(
                nombre=safe_string(row["nombre"]),
                nombre_corto=row["nombre_corto"],
                icono=row["icono"],
                ruta=row["ruta"],
                en_navegacion=row["en_navegacion"] == "1",
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} módulos alimentados.")
