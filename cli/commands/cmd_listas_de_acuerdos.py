"""
Listas de Acuerdos

- refrescar: Rastrear el depósito para agregar las que no tiene y dar de baja las que no existen en la BD
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad

app = create_app()
db.app = app


@click.group()
def cli():
    """Listas de Acuerdos"""


# @click.command()
# @click.argument("autoridad_email", type=str)
# @click.argument("fecha", type=str)
# @click.argument("archivo", type=str)
# @click.option("--descripcion", default="", type=str)
# @click.option("--url", default="", type=str)
# def agregar(autoridad_email, fecha, archivo, descripcion=None, url=None):
#     """Agregar una lista de acuerdos que se recibió vía correo electrónico"""
#     resultado = app.task_queue.enqueue(
#         "plataforma_web.blueprints.listas_de_acuerdos.tasks.agregar",
#         usuario_id=None,
#         autoridad_email=autoridad_email,
#         fecha=fecha,
#         archivo=archivo,
#         descripcion=descripcion,
#         url=url,
#     )
#     click.echo(f"Se ha lanzado la tarea en el fondo {resultado}")


@click.command()
@click.argument("autoridad_clave", type=str)
def refrescar(autoridad_clave):
    """Rastrear el depósito para agregar las que no tiene y dar de baja las que no existen en la BD"""
    autoridad = Autoridad.query.filter(Autoridad.clave == autoridad_clave).first()
    if autoridad is None:
        click.echo(f"No existe la clave {autoridad_clave} en autoridades")
        return
    click.echo(f"- {autoridad.distrito.nombre}")
    click.echo(f"- {autoridad.descripcion}")
    app.task_queue.enqueue(
        "plataforma_web.blueprints.listas_de_acuerdos.tasks.refrescar",
        autoridad_id=autoridad.id,
        usuario_id=None,
    )
    click.echo("Refrescar se está ejecutando en el fondo.")


# cli.add_command(agregar)
cli.add_command(refrescar)
