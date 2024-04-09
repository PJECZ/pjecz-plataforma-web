"""
Sentencias

- respaldar: Respaldar a un archivo CSV
"""

from datetime import datetime
from pathlib import Path
import csv
import click

from lib.safe_string import extract_expediente_anio, extract_expediente_num

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.sentencias.models import Sentencia

app = create_app()
db.app = app


@click.group()
def cli():
    """Sentencias"""


@click.command()
def enviar_reporte():
    """Enviar via correo electronico el reporte de sentencias"""
    app.task_queue.enqueue(
        "plataforma_web.blueprints.sentencias.tasks.enviar_reporte",
    )
    click.echo("Enviar reporte de sentencias se está ejecutando en el fondo.")


@click.command()
@click.option("--autoridad-id", default=None, type=int, help="ID de la autoridad")
@click.option("--autoridad-clave", default="", type=str, help="Clave de la autoridad")
@click.option("--desde", default="", type=str, help="Fecha de inicio AAAA-MM-DD")
@click.option("--output", default="sentencias.csv", type=str, help="Archivo CSV a escribir")
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
    click.echo("Respaldando sentencias...")
    contador = 0
    sentencias = Sentencia.query.filter_by(estatus="A")
    if autoridad is not None:
        sentencias = sentencias.filter(Sentencia.autoridad == autoridad)
    if desde_fecha is not None:
        sentencias = sentencias.filter(Sentencia.fecha >= desde_fecha)
    sentencias = sentencias.order_by(Sentencia.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "sentencia_id",
                "autoridad_clave",
                "materia_tipo_juicio",
                "sentencia",
                "sentencia_fecha",
                "expediente",
                "fecha",
                "descripcion",
                "es_perspectiva_genero",
                "archivo",
                "url",
            ]
        )
        for sentencia in sentencias:
            respaldo.writerow(
                [
                    sentencia.id,
                    sentencia.autoridad.clave,
                    sentencia.materia_tipo_juicio.descripcion,
                    sentencia.sentencia,
                    sentencia.sentencia_fecha,
                    sentencia.expediente,
                    sentencia.fecha,
                    sentencia.descripcion,
                    sentencia.es_perspectiva_genero,
                    sentencia.archivo,
                    sentencia.url,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} sentencias en {ruta.name}")


@click.command()
def actualizar_expedientes_anios_nums():
    """Actualizar el anio y el numero de los expedientes"""
    click.echo("Actualizar el anio y el numero de los expedientes")
    database = db.session
    contador = 0
    sentencias = Sentencia.query.filter_by(estatus="A")
    for sentencia in sentencias:
        if sentencia.expediente_anio is None or sentencia.expediente_num is None:
            anio = extract_expediente_anio(sentencia.expediente)
            if anio != 0:
                sentencia.expediente_anio = anio
            num = extract_expediente_num(sentencia.expediente)
            if num != 0:
                sentencia.expediente_num = num
            if anio != 0 and num != 0:
                database.add(sentencia)
            contador += 1
            if contador % 100 == 0:
                database.commit()
                click.echo(f"  Van {contador}...")
    if contador > 0 and contador % 100 != 0:
        database.commit()
    click.echo(f"Actualizados {contador} sentencias")


cli.add_command(enviar_reporte)
cli.add_command(respaldar)
cli.add_command(actualizar_expedientes_anios_nums)
