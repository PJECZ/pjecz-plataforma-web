"""
Archivos

- actualizar_expedientes_anios_nums: Descompone el num-expedientes en número y año, y lo guarda individualmente como números.
- pasar_al_historial: Pasa al historial las solicitudes entregadas y las remesas procesadas después de varios días.
"""
import click

from lib.safe_string import extract_expediente_anio, extract_expediente_num

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento

app = create_app()
db.app = app


@click.group()
def cli():
    """Archivos"""


@click.command()
def actualizar_expedientes_anios_nums():
    """Actualizar el anio y el numero de los expedientes"""
    click.echo("Actualizar el anio y el numero de los expedientes")
    database = db.session
    contador = 0
    documentos = ArcDocumento.query.filter_by(estatus="A")
    for documento in documentos:
        if documento.anio is None or documento.expediente_numero is None:
            anio = extract_expediente_anio(documento.expediente)
            if anio != 0:
                documento.anio = anio
            num = extract_expediente_num(documento.expediente)
            if num != 0:
                documento.expediente_numero = num
            if anio != 0 and num != 0:
                database.add(documento)
            else:
                click.echo(f"!  Error en expediente ID[{documento.id}]: '{documento.expediente}'")
            contador += 1
            if contador % 100 == 0:
                database.commit()
                click.echo(f"  Van {contador}...")
    if contador > 0 and contador % 100 != 0:
        database.commit()
    click.echo(f"Actualizados {contador} documentos")


@click.command()
def pasar_al_historial():
    """Pasar al historial las solicitudes y remesas con mucha antigüedad habiendo sido procesadas correctamente"""

    app.task_queue.enqueue(
        "plataforma_web.blueprints.arc_archivos.tasks.pasar_al_historial_solicitudes_remesas",
    )
    click.echo("Pasar al historial las solicitudes y remesas atendidas.")


cli.add_command(actualizar_expedientes_anios_nums)
cli.add_command(pasar_al_historial)
