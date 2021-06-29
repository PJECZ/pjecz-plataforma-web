"""
Distritos

- alimentar: Alimentar la tabla insertando registros desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito

app = create_app()
db.app = app


@click.group()
def cli():
    """Distritos"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar la tabla insertando registros desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando distritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Distrito(
                nombre=row["nombre"],
                nombre_corto=row["nombre_corto"],
                es_distrito_judicial=(row["es_distrito_judicial"] == "1"),
                estatus=row["estatus"],
            ).save()
            contador += 1
    click.echo(f"{contador} distritos alimentados.")


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando distritos...")
    contador = 0
    distritos = Distrito.query.order_by(Distrito.id).all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(["id", "nombre", "nombre_corto", "es_distrito_judicial", "estatus"])
        for distrito in distritos:
            escritor.writerow(
                [
                    distrito.id,
                    distrito.nombre,
                    distrito.nombre_corto,
                    int(distrito.es_distrito_judicial),
                    distrito.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} distritos.")


cli.add_command(alimentar)
cli.add_command(respaldar)
