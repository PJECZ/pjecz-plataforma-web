"""
REDAM (Registro Estatal de Deudores Alimentarios)

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from lib.safe_string import safe_expediente, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.redams.models import Redam

app = create_app()
db.app = app


@click.group()
def cli():
    """REDAM"""


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
    autoridad_no_definida = Autoridad.query.filter_by(clave="ND").first()
    if autoridad_no_definida is None:
        click.echo("AVISO: No hay autoridad con clave ND.")
        return
    click.echo("Alimentando deudores alimentarios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            if "autoridad_clave" in row:
                autoridad_clave = row["autoridad_clave"]
                autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
                if autoridad is None:
                    autoridad = autoridad_no_definida
                    click.echo(f"No existe la clave de autoridad {autoridad_clave}")
            nombre = safe_string(row["nombre"])
            if nombre == "":
                continue
            try:
                expediente = safe_expediente(row["expediente"])
            except (IndexError, ValueError):
                click.echo(f"No es correcto el expediente {row['expediente']}")
                continue
            try:
                fecha = datetime.strptime(row["fecha"], "%Y-%m-%d")
            except (ValueError, TypeError):
                click.echo(f"No es correcta la fecha {row['fecha']}")
                continue
            Redam(
                autoridad=autoridad,
                nombre=nombre,
                expediente=expediente,
                fecha=fecha,
                observaciones=safe_string(row["observaciones"], max_len=1024),
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} deudores alimentarios.")


@click.command()
@click.option("--output", default="redam.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""


cli.add_command(alimentar)
cli.add_command(respaldar)
