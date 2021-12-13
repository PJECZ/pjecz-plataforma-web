"""
Identidades de Géneros

- alimentar: Alimentar desde un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from lib.safe_string import safe_expediente, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.identidades_generos.models import IdentidadGenero

app = create_app()
db.app = app


@click.group()
def cli():
    """Identiades de Géneros"""


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
    click.echo("Alimentando identidades de géneros...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                procedimiento = safe_expediente(row["procedimiento"])
            except (IndexError, ValueError):
                click.echo(f"  AVISO: {procedimiento} no es válido.")
                continue
            try:
                fecha_nacimiento = datetime.strptime(row["fechaNacimiento"][:10], "%Y-%m-%d")
            except ValueError:
                click.echo(f"  AVISO: {row['fechaNacimiento']} no es una fecha válida.")
                continue
            genero_actual=safe_string(row["generoActual"])
            if genero_actual == "M":
                genero_actual = "MASCULINO"
            elif genero_actual == "F":
                genero_actual = "FEMENINO"
            genero_anterior=safe_string(row["generoAnterior"])
            if genero_anterior == "M":
                genero_anterior = "MASCULINO"
            elif genero_anterior == "F":
                genero_anterior = "FEMENINO"
            IdentidadGenero(
                procedimiento=procedimiento,
                fecha_nacimiento=fecha_nacimiento,
                nombre_anterior=safe_string(row["nombreAnterior"]),
                genero_anterior=genero_anterior,
                nombre_actual=safe_string(row["nombreActual"]),
                genero_actual=genero_actual,
                lugar_nacimiento=safe_string(row["lugarNacimiento"]),
                nombre_padre=safe_string(row["padre"]),
                nombre_madre=safe_string(row["madre"]),
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} identidades de géneros alimentadas.")

cli.add_command(alimentar)
