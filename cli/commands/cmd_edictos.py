"""
Edictos

- borrar: Borrar todos los registros
- refrescar: Rastrear el depósito para agregar o dar de baja
- refrescar_todos: Rastrear el depósito para agregar o dar de baja
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.edictos.models import Edicto

app = create_app()
db.app = app


@click.group()
def cli():
    """Edictos"""


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
    if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
        click.echo(f"La autoridad {autoridad_clave} no tiene directorio para edictos")
        return
    app.task_queue.enqueue(
        "plataforma_web.blueprints.edictos.tasks.refrescar",
        autoridad_id=autoridad.id,
        usuario_id=None,
    )
    click.echo(f"Refrescar Edictos de {autoridad.clave} se está ejecutando en el fondo.")


@click.command()
def refrescar_todos():
    """Rastrear el depósito para agregar o dar de baja"""
    contador = 0
    autoridades = Autoridad.query.filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    for autoridad in autoridades:
        if not autoridad.distrito.es_distrito_judicial:
            continue
        if not autoridad.es_jurisdiccional:
            continue
        if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
            continue
        app.task_queue.enqueue(
            "plataforma_web.blueprints.edictos.tasks.refrescar",
            autoridad_id=autoridad.id,
            usuario_id=None,
        )
        click.echo(f"- Refrescar Edictos a {autoridad.clave}")
        contador += 1
    click.echo(f"Se lanzaron {contador} tareas para ejecutar en el fondo.")


@click.command()
def borrar():
    """Borrar todos los registros"""
    click.echo("Borrando los edictos en la base de datos...")
    cantidad = db.session.query(Edicto).delete()
    db.session.commit()
    click.echo(f"Han sido borrados {str(cantidad)} registros.")


cli.add_command(refrescar)
cli.add_command(refrescar_todos)
cli.add_command(borrar)
