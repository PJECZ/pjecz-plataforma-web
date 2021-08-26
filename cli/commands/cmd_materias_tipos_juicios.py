"""
Materias Tipos Juicios

- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio

app = create_app()
db.app = app


@click.group()
def cli():
    """Materias Tipos Juicios"""


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando materias tipos juicios...")
    contador = 0
    materias_tipos_juicios = MateriaTipoJuicio.query.order_by(MateriaTipoJuicio.id).all()
    with open(ruta, "w") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "materia_id", "nombre", "estatus"])
        for materia in materias_tipos_juicios:
            respaldo.writerow(
                [
                    materia.id,
                    materia.materia_id,
                    materia.descripcion,
                    materia.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} materias tipos juicios.")


cli.add_command(respaldar)
