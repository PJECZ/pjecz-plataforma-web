"""
Estadisticas Variables

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv

import click

from lib.safe_string import safe_string, safe_clave

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.est_variables.models import EstVariable

app = create_app()
db.app = app


@click.group()
def cli():
    """Estadisticas Variables"""


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
    click.echo("Alimentando variables...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                clave = safe_clave(row["clave"])
                descripcion = safe_string(row["descripcion"], save_enie=True, to_uppercase=False, do_unidecode=False)
            except (IndexError, ValueError):
                click.echo("  Dato incorrecto: " + str(row))
                continue
            EstVariable(clave=clave, descripcion=descripcion).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} variables alimentadas.")


@click.command()
@click.option("--output", default="est_variables.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando variables...")
    contador = 0
    est_variables = EstVariable.query.filter_by(estatus="A")
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["est_variable_id", "clave", "descripcion"])
        for est_variable in est_variables:
            respaldo.writerow(
                [
                    est_variable.id,
                    est_variable.clave,
                    est_variable.descripcion,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} variables en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)
