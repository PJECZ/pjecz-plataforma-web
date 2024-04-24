"""
Municipios

- alimentar: Alimentar desde un archivo CSV
"""
from pathlib import Path
import csv

import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.estados.models import Estado
from plataforma_web.blueprints.municipios.models import Municipio

app = create_app()
db.app = app


@click.group()
def cli():
    """Municipios"""


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
    click.echo("Alimentando municipios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                estado_clave = row["estado_clave"]
                municipio_clave = row["municipio_clave"]
                municipio_nombre = row["municipio_nombre"]
            except (IndexError, ValueError):
                click.echo("  Dato incorrecto: " + str(row))
                continue
            estado = Estado.query.filter_by(clave=estado_clave).filter_by(estatus="A").first()
            if estado is None:
                click.echo(f"  AVISO: El estado con la clave {estado_clave} no se encuentra")
                continue
            municipio = Municipio.query.filter_by(estado=estado).filter_by(clave=municipio_clave).filter_by(estatus='A').first()
            if municipio:
                click.echo(f"  AVISO: El municipio {municipio_nombre} con clave {municipio_clave} ya se encuentra alimentado")
                continue
            datos = {
                "clave": municipio_clave,
                "nombre": safe_string(municipio_nombre),
                "estado": estado,
            }
            Municipio(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} municipios alimentados.")

cli.add_command(alimentar)
