"""
Modulos

- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.modulos.models import Modulo

app = create_app()
db.app = app


@click.group()
def cli():
    """Modulos"""


@click.command()
@click.option("--output", default="modulos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando módulos...")
    contador = 0
    modulos = Modulo.query.order_by(Modulo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "id",
                "nombre",
                "nombre_corto",
                "icono",
                "ruta",
                "en_navegacion",
                "estatus",
            ]
        )
        for modulo in modulos:
            if modulo.en_navegacion:
                en_navegacion = "1"
            else:
                en_navegacion = ""
            respaldo.writerow(
                [
                    modulo.id,
                    modulo.nombre,
                    modulo.nombre_corto,
                    modulo.icono,
                    modulo.ruta,
                    en_navegacion,
                    modulo.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} módulos en {ruta.name}")


cli.add_command(respaldar)
