"""
Alimentar inventarios redes
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_redes.models import InvRed

INV_REDES_CSV = "seed/inv_redes.csv"


def alimentar_inv_redes():
    """Alimentar inventarios redes"""
    ruta = Path(INV_REDES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando inventarios redes...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            inv_red_id = int(row["inv_red_id"])
            if inv_red_id != contador + 1:
                click.echo(f"  AVISO: inv_red_id {inv_red_id} no es consecutivo")
                continue
            InvRed(
                nombre=safe_string(row["nombre"], save_enie=True),
                tipo=safe_string(row["tipo"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} redes alimentadas")
