"""
Materias

- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.materias.models import Materia

app = create_app()
db.app = app


@click.group()
def cli():
    """Materias"""


@click.command()
@click.option("--output", default="materias.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando materias...")
    contador = 0
    materias = Materia.query.order_by(Materia.id).all()
    with open(ruta, "w") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "nombre", "estatus"])
        for materia in materias:
            respaldo.writerow(
                [
                    materia.id,
                    materia.nombre,
                    materia.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} materias en {ruta.name}")


cli.add_command(respaldar)
