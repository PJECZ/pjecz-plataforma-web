"""
Distritos

- alimentar: Alimentar insertando registros desde un archivo CSV
- borrar: Borrar todos los registros
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
    """Alimentar la tabla distritos insertando registros desde un archivo CSV"""


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar la tabla distritos a su archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando distritos...")
    contador = 0
    distritos = Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(["id", "nombre", "nombre_corto", "es_distrito_judicial"])
        for distrito in distritos:
            escritor.writerow(
                [
                    distrito.id,
                    distrito.nombre,
                    distrito.nombre_corto,
                    int(distrito.es_distrito_judicial),
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} registros.")


@click.command()
def borrar():
    """Borrar todos los registros"""
    click.echo("Borrando los distritos en la base de datos...")
    cantidad = db.session.query(Distrito).delete()
    db.session.commit()
    click.echo(f"Han sido borrados {str(cantidad)} registros.")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(borrar)
