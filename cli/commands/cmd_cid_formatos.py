"""
CID Formatos

- respaldar: Respaldar formatos autorizados a un archivo CSV
"""
import csv
from datetime import datetime
from pathlib import Path

import click

from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

from plataforma_web.app import create_app
from plataforma_web.extensions import db


app = create_app()
db.app = app


@click.group()
def cli():
    """CID Formatos"""


@click.command()
def respaldar():
    """Respaldar formatos autorizados a un archivo CSV"""
    click.echo("Respaldando formatos...")
    salida = Path(f"cid_formatos-{datetime.now().strftime('%Y-%m-%d')}.csv")
    contador = 0
    cid_formatos = CIDFormato.query.join(CIDProcedimiento).filter_by(estatus="A").filter(CIDProcedimiento.seguimiento == "AUTORIZADO").all()
    with open(salida, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "descripcion", "procedimiento_id", "procedimiento_titulo", "procedimiento_codigo", "procedimiento_fecha", "autoridad_clave", "autoridad_seguimiento", "url"])
        for cid_formato in cid_formatos:
            respaldo.writerow(
                [
                    cid_formato.id,
                    cid_formato.descripcion,
                    cid_formato.procedimiento_id,
                    cid_formato.procedimiento.titulo_procedimiento,
                    cid_formato.procedimiento.codigo,
                    cid_formato.procedimiento.fecha,
                    cid_formato.procedimiento.autoridad.clave,
                    cid_formato.procedimiento.seguimiento,
                    cid_formato.url,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} formatos en {salida}")


cli.add_command(respaldar)
