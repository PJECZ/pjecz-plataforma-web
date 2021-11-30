"""
Sentencias

- refrescar: Rastrear el depósito para agregar o dar de baja
- refrescar_todos: Rastrear el depósito para agregar o dar de baja
- respaldar: Respaldar a un archivo CSV
"""
from datetime import datetime
from pathlib import Path
import csv
import click

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
@click.argument("autoridad_clave", type=str)
def refrescar(autoridad_clave):
    """Rastrear el depósito para agregar o dar de baja"""
    autoridad = Autoridad.query.filter(Autoridad.clave == autoridad_clave).first()
    if autoridad is None:
        click.echo(f"No existe la clave {autoridad_clave} en autoridades")
        return
    if not autoridad.distrito.es_distrito_judicial:
        click.echo(f"La autoridad {autoridad_clave} no está en un distrito judicial")
        return
    if not autoridad.es_jurisdiccional:
        click.echo(f"La autoridad {autoridad_clave} no es jurisdiccional")
        return
    if autoridad.es_notaria:
        click.echo(f"La autoridad {autoridad_clave} es una notaría")
        return
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        click.echo(f"La autoridad {autoridad_clave} no tiene directorio para listas de acuerdos")
        return
    app.task_queue.enqueue(
        "plataforma_web.blueprints.sentencias.tasks.refrescar",
        autoridad_id=autoridad.id,
        usuario_id=None,
    )
    click.echo(f"Refrescar Sentencias de {autoridad.clave} se está ejecutando en el fondo.")


@click.command()
def refrescar_todos():
    """Rastrear el depósito para agregar o dar de baja"""
    contador = 0
    autoridades = Autoridad.query.filter_by(estatus="A").order_by(Autoridad.clave).all()
    for autoridad in autoridades:
        if not autoridad.distrito.es_distrito_judicial:
            continue
        if not autoridad.es_jurisdiccional:
            continue
        if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
            continue
        app.task_queue.enqueue(
            "plataforma_web.blueprints.sentencias.tasks.refrescar",
            autoridad_id=autoridad.id,
            usuario_id=None,
        )
        click.echo(f"- Refrescar Sentencias a {autoridad.clave}")
        contador += 1
    click.echo(f"Se lanzaron {contador} tareas para ejecutar en el fondo.")


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
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} sentencias en {ruta.name}")


cli.add_command(enviar_reporte)
cli.add_command(refrescar)
cli.add_command(refrescar_todos)
cli.add_command(respaldar)
