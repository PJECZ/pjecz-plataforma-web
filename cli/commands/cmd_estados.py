"""
Estados

- alimentar: Alimentar desde un archivo CSV
"""

from pathlib import Path
import csv

import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.estados.models import Estado

app = create_app()
db.app = app


@click.group()
def cli():
    """Estados"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando estados...")
    contador = 0
    contador_omitidos = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                clave = row["estado_clave"].zfill(2)
                nombre = safe_string(row["estado_nombre"], save_enie=True)
            except (IndexError, ValueError):
                click.echo("  Dato incorrecto: " + str(row))
                continue
            estado = Estado.query.filter_by(clave=clave).filter_by(estatus="A").first()
            if estado:
                contador_omitidos += 1
                continue
            datos = {
                "clave": clave,
                "nombre": nombre,
            }
            Estado(**datos).save()
            contador += 1
            click.echo(f"  {clave} {nombre}")
    click.echo(f"Se han alimentado {contador} estados.")
    click.echo(f"Se han omitido {contador_omitidos} renglones.")


cli.add_command(alimentar)
