"""
Listas de Acuerdos

- enviar_reporte: Enviar via correo electronico el reporte de listas de acuerdos
- refrescar: Rastrear el depósito para agregar o dar de baja
- refrescar_todos: Rastrear el depósito para agregar o dar de baja
"""
from datetime import datetime
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad

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


cli.add_command(enviar_reporte)
cli.add_command(refrescar)
cli.add_command(refrescar_todos)
