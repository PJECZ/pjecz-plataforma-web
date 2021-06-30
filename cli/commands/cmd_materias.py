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
    """Materia"""


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando materias...")
    contador = 0
    materias = Materia.query.order_by(Materia.id).all()
    with open(ruta, "w") as puntero:
        materia = csv.writer(puntero)
        materia.writerow(["id", "nombre", "estatus"])
        for distrito in materias:
            materia.writerow(
                [
                    distrito.id,
                    distrito.nombre,
                    distrito.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} materias.")


cli.add_command(respaldar)
