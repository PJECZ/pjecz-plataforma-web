"""
Peritos Tipos

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo

app = create_app()
db.app = app


@click.group()
def cli():
    """Peritos Tipos"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar a partir de un archivo CSV"""
    ruta = Path(entrada_csv)
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


@click.command()
@click.option("--output", default="peritos-tipos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {output} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando tipos de peritos...")
    contador = 0
    peritos_tipos = PeritoTipo.query.order_by(PeritoTipo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "materia_id",
                "nombre",
                "estatus",
            ]
        )
        for perito_tipo in peritos_tipos:
            respaldo.writerow(
                [
                    perito_tipo.id,
                    perito_tipo.nombre,
                    perito_tipo.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} peritos_tipos en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)
