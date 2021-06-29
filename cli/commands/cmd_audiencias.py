"""
Abogados

- alimentar: Alimentar insertando registros desde un archivo CSV
- borrar: Borrar todos los registros
- respaldar: Respaldar a un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click
from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.autoridades.models import Autoridad

app = create_app()
db.app = app


@click.group()
def cli():
    """Audiencias"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar la tabla audiencias insertando registros desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    clave = ruta.name[: -len(ruta.suffix)]
    autoridad = Autoridad.query.filter(Autoridad.clave == clave).first()
    if autoridad is None:
        click.echo(f"AVISO: {ruta.name} no se encuentra esa clave en autoridades.")
        return
    click.echo("Alimentando audiencias...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                tiempo = datetime.strptime(row["tiempo"], '%Y-%m-%d %H:%M')
            except (IndexError, ValueError):
                pass
            datos = {
                "autoridad": autoridad,
                "tiempo": tiempo,
                "tipo_audiencia": safe_string(row["tipo_audiencia"]),
                "expediente": safe_string(row["expediente"]),
                "xxxx": safe_string(row["xxxx"]),
                "xxxx": safe_string(row["xxxx"]),
            }
            Audiencia(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} ubicaciones de expedientes...")
    click.echo(f"{contador} audiencias alimentadas.")


@click.command()
@click.argument("salida_csv")
@click.option("--desde", default="", type=str, help="Fecha de inicio, use AAAA-MM-DD")
def respaldar(desde, salida_csv):
    """Respaldar la tabla audiencias a su archivo CSV"""


@click.command()
def borrar():
    """Borrar todos los registros"""
    click.echo("Borrando las audiencias en la base de datos...")
    cantidad = db.session.query(Audiencia).delete()
    db.session.commit()
    click.echo(f"Han sido borrados {str(cantidad)} registros.")
