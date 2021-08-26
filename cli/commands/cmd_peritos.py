"""
Peritos

- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.peritos.models import Perito

app = create_app()
db.app = app


@click.group()
def cli():
    """Peritos"""


@click.command()
@click.option("--output", default="peritos.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando peritos...")
    contador = 0
    peritos = Perito.query.filter_by(estatus="A").order_by(Perito.distrito_id, Perito.tipo, Perito.nombre).all()
    with open(ruta, "w") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["distrito_id", "tipo", "nombre", "domicilio", "telefono_fijo", "telefono_celular", "email", "renovacion", "notas"])
        for perito in peritos:
            respaldo.writerow(
                [
                    perito.distrito_id,
                    perito.tipo,
                    perito.nombre,
                    perito.domicilio,
                    perito.telefono_fijo,
                    perito.telefono_celular,
                    perito.email,
                    perito.renovacion.strftime("%Y-%m-%d"),
                    perito.notas,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} peritos en {ruta.name}")


cli.add_command(respaldar)
