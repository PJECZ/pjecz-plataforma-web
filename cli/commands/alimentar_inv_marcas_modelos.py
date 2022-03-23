"""
Alimentar inventarios marcas y modelos
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.inv_modelos.models import InvModelo

INV_MARCAS_MODELOS_CSV = "seed/inv_marcas_modelos.csv"


def alimentar_inv_marcas_modelos():
    """Alimentar inventarios categorias"""
    ruta = Path(INV_MARCAS_MODELOS_CSV)
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
            inv_modelo_id = int(row["inv_modelo_id"])
            if inv_modelo_id != contador + 1:
                click.echo(f"  AVISO: inv_modelo_id {inv_modelo_id} no es consecutivo")
                continue
            marca = InvMarca.query.filter_by(nombre=safe_string(row["marca_nombre"])).first()
            if marca is None:
                marca = InvMarca(nombre=safe_string(row["marca_nombre"]))
                marca.save()
            InvModelo(
                marca=marca,
                descripcion=safe_string(row["modelo_descripcion"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} inventarios categorias alimentadas")
