"""
Peritos

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo

app = create_app()
db.app = app


@click.group()
def cli():
    """Peritos"""


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
    click.echo("Alimentando peritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                distrito_nombre = row["distrito_nombre"]
                perito_tipo_nombre = safe_string(row["perito_tipo_nombre"])
                nombre = safe_string(row["nombre"])
                domicilio = safe_string(row["domicilio"])
                telefono_fijo = safe_string(row["telefono_fijo"])
                telefono_celular = safe_string(row["telefono_celular"])
                email = row["email"]
                renovacion = datetime.strptime(row["renovacion"], "%Y-%m-%d")
                notas = safe_string(row["notas"])
            except ValueError:
                click.echo("  Dato incorrecto: " + str(row))
                continue
            distrito = Distrito.query.filter_by(nombre=distrito_nombre).first()
            if distrito is None:
                click.echo(f"AVISO: No existe el distrito {distrito_nombre}")
                continue
            perito_tipo = PeritoTipo.query.filter_by(nombre=perito_tipo_nombre).first()
            if perito_tipo is None:
                click.echo(f"AVISO: No existe el tipo de perito {perito_tipo_nombre}")
                continue
            Perito(
                distrito=distrito,
                perito_tipo=perito_tipo,
                nombre=nombre,
                domicilio=domicilio,
                telefono_fijo=telefono_fijo,
                telefono_celular=telefono_celular,
                email=email,
                renovacion=renovacion,
                notas=notas,
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} peritos alimentados.")


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
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "perito_id",
                "distrito_nombre",
                "perito_tipo_nombre",
                "nombre",
                "domicilio",
                "telefono_fijo",
                "telefono_celular",
                "email",
                "renovacion",
                "notas",
            ]
        )
        for perito in peritos:
            respaldo.writerow(
                [
                    perito.id,
                    perito.distrito.nombre,
                    perito.perito_tipo.nombre,
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
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} peritos en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)
