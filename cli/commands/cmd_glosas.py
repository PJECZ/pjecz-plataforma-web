"""
Glosas

- respaldar: Respaldar a un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.glosas.models import Glosa

app = create_app()
db.app = app


@click.group()
def cli():
    """Glosas"""


@click.command()
@click.option("--autoridad-id", default=None, type=int, help="ID de la autoridad")
@click.option("--autoridad-clave", default="", type=str, help="Clave de la autoridad")
@click.option("--desde", default="", type=str, help="Fecha de inicio AAAA-MM-DD")
@click.option("--output", default="glosas.csv", type=str, help="Archivo CSV a escribir")
def respaldar(autoridad_id, autoridad_clave, desde, output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    if autoridad_id:
        autoridad = Autoridad.query.get(autoridad_id)
    elif autoridad_clave:
        autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
    else:
        autoridad = None
    if desde != "":
        try:
            desde_fecha = datetime.strptime(desde, "%Y-%m-%d")
        except ValueError as mensaje:
            click.echo(f"AVISO: Fecha de inicio es incorrecta: {mensaje}")
            return
    else:
        desde_fecha = None
    click.echo("Respaldando glosas...")
    contador = 0
    glosas = Glosa.query.filter_by(estatus="A")
    if autoridad is not None:
        glosas = glosas.filter(Glosa.autoridad == autoridad)
    if desde_fecha is not None:
        glosas = glosas.filter(Glosa.fecha >= desde_fecha)
    glosas = glosas.order_by(Glosa.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "glosa_id",
                "autoridad_clave",
                "fecha",
                "tipo_juicio",
                "descripcion",
                "expediente",
                "archivo",
                "url",
            ]
        )
        for glosa in glosas:
            respaldo.writerow(
                [
                    glosa.id,
                    glosa.autoridad.clave,
                    glosa.fecha,
                    glosa.tipo_juicio,
                    glosa.descripcion,
                    glosa.expediente,
                    glosa.archivo,
                    glosa.url,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldadas {contador} glosas en {ruta.name}")


cli.add_command(respaldar)
