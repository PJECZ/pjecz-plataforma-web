"""
Alimentar inventarios categorias
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_categorias.models import InvCategoria

INV_CATEGORIAS_CSV = "seed/inv_categorias.csv"


def alimentar_inv_categorias():
    """Alimentar inventarios categorias"""
    ruta = Path(INV_CATEGORIAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando inventarios categorias...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            inv_categoria_id = int(row["inv_categoria_id"])
            if inv_categoria_id != contador + 1:
                click.echo(f"  AVISO: inv_categoria_id {inv_categoria_id} no es consecutivo")
                continue
            InvCategoria(
                nombre=safe_string(row["nombre"], save_enie=True),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} categorias alimentadas")
