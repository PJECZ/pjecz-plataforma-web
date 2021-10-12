"""
Listas de Acuerdos

- enviar_reporte: Enviar via correo electronico el reporte de listas de acuerdos
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
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

app = create_app()
db.app = app


@click.group()
def cli():
    """Listas de Acuerdos"""


@click.command()
@click.option("--fecha", default="", type=str, help="Fecha a consultar")
def enviar_reporte(fecha):
    """Enviar via correo electronico el reporte de listas de acuerdos"""
    if fecha != "":
        try:
            fecha_date = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError as mensaje:
            click.echo(f"AVISO: Fecha incorrecta {mensaje}")
            return
    else:
        fecha_date = None
    app.task_queue.enqueue(
        "plataforma_web.blueprints.listas_de_acuerdos.tasks.enviar_reporte",
        fecha=fecha_date,
    )
    click.echo("Enviar reporte de listas de acuerdo se está ejecutando en el fondo.")


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
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        click.echo(f"La autoridad {autoridad_clave} no tiene directorio para listas de acuerdos")
        return
    app.task_queue.enqueue(
        "plataforma_web.blueprints.listas_de_acuerdos.tasks.refrescar",
        autoridad_id=autoridad.id,
        usuario_id=None,
    )
    click.echo(f"Refrescar Listas de Acuerdos de {autoridad.clave} se está ejecutando en el fondo.")


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
        if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
            continue
        app.task_queue.enqueue(
            "plataforma_web.blueprints.listas_de_acuerdos.tasks.refrescar",
            autoridad_id=autoridad.id,
            usuario_id=None,
        )
        click.echo(f"- Refrescar Listas de Acuerdos a {autoridad.clave}")
        contador += 1
    click.echo(f"Se lanzaron {contador} tareas para ejecutar en el fondo.")


@click.command()
@click.option("--autoridad-id", default=None, type=int, help="ID de la autoridad")
@click.option("--autoridad-clave", default="", type=str, help="Clave de la autoridad")
@click.option("--desde", default="", type=str, help="Fecha de inicio AAAA-MM-DD")
@click.option("--output", default="listas_de_acuerdos.csv", type=str, help="Archivo CSV a escribir")
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
    click.echo("Respaldando listas de acuerdos...")
    contador = 0
    listas_de_acuerdos = ListaDeAcuerdo.query.filter_by(estatus="A")
    if autoridad is not None:
        listas_de_acuerdos = listas_de_acuerdos.filter(ListaDeAcuerdo.autoridad == autoridad)
    if desde_fecha is not None:
        listas_de_acuerdos = listas_de_acuerdos.filter(ListaDeAcuerdo.fecha >= desde_fecha)
    listas_de_acuerdos = listas_de_acuerdos.order_by(ListaDeAcuerdo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "autoridad_clave",
                "fecha",
                "descripcion",
                "archivo",
                "url",
            ]
        )
        for lista_de_acuerdo in listas_de_acuerdos:
            respaldo.writerow(
                [
                    lista_de_acuerdo.autoridad.clave,
                    lista_de_acuerdo.fecha,
                    lista_de_acuerdo.descripcion,
                    lista_de_acuerdo.archivo,
                    lista_de_acuerdo.url,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldadas {contador} listas de acuerdos en {ruta.name}")


cli.add_command(enviar_reporte)
cli.add_command(refrescar)
cli.add_command(refrescar_todos)
cli.add_command(respaldar)
