"""
CID Procedimientos

- crear_pdf: Crear PDF
- respaldar: Respaldar formatos autorizados a un archivo CSV
"""
import csv
from datetime import datetime
from pathlib import Path

import click

from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
def cli():
    """CID Procedimientos"""


@click.command()
@click.argument("cid_procedimiento_id", type=int)
def crear_pdf(cid_procedimiento_id):
    """Crear PDF"""
    app.task_queue.enqueue(
        "plataforma_web.blueprints.cid_procedimientos.tasks.crear_pdf",
        cid_procedimiento_id=cid_procedimiento_id,
    )
    click.echo("Crear PDF se está ejecutando en el fondo.")


@click.command()
def respaldar():
    """Respaldar formatos autorizados a un archivo CSV"""
    click.echo("Respaldando Procedimientos...")
    salida = Path(f"cid_procedimientos-{datetime.now().strftime('%Y-%m-%d')}.csv")
    contador = 0
    cid_procedimientos = CIDProcedimiento.query.filter_by(estatus="A").filter_by(seguimiento="AUTORIZADO").all()
    with open(salida, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "titulo", "codigo", "fecha", "autoridad_clave", "seguimiento", "url"])
        for cid_procedimiento in cid_procedimientos:
            respaldo.writerow(
                [
                    cid_procedimiento.id,
                    cid_procedimiento.titulo_procedimiento,
                    cid_procedimiento.codigo,
                    cid_procedimiento.fecha,
                    cid_procedimiento.autoridad.clave,
                    cid_procedimiento.seguimiento,
                    cid_procedimiento.url,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} procedimientos en {salida}")


cli.add_command(crear_pdf)
cli.add_command(respaldar)
