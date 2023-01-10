"""
Estadisticas Acuerdos

- alimentar: Insertar acuerdos a partir de un archivo CSV
"""
import csv
from datetime import datetime
from pathlib import Path

import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.est_acuerdos.models import EstAcuerdo

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app


@click.group()
@click.pass_context
def cli(ctx):
    """Estadisticas Acuerdos"""


@click.command()
@click.argument("archivo_csv", type=str)
@click.pass_context
def alimentar(ctx, archivo_csv):
    """Insertar equipos a partir de un archivo CSV"""

    # Validar que exista el archivo CSV
    archivo = Path(archivo_csv)
    if not archivo.exists():
        click.echo(f"ERROR: No existe el archivo {archivo_csv}")
        ctx.exit(1)

    # Leer archivo CSV
    contador = 0
    with open(archivo_csv, "r", encoding="UTF8") as puntero:
        renglones = csv.DictReader(puntero)
        for renglon in renglones:

            # Debe de estar distrito_nombre en el renglon
            if "distrito_nombre" not in renglon:
                click.echo("ERROR: Falta distrito_nombre en el archivo CSV")
                ctx.exit(1)

            # Debe de estar autoridad_descripcion en el renglon
            if "autoridad_descripcion" not in renglon:
                click.echo("ERROR: Falta autoridad_descripcion en el archivo CSV")
                ctx.exit(1)

            # Debe de estar folio en el renglon
            if "folio" not in renglon:
                click.echo("ERROR: Falta folio en el archivo CSV")
                ctx.exit(1)

            # Debe de estar expediente en el renglon
            if "expediente" not in renglon:
                click.echo("ERROR: Falta expediente en el archivo CSV")
                ctx.exit(1)

            # Debe de estar numero_caso en el renglon
            if "numero_caso" not in renglon:
                click.echo("ERROR: Falta numero_caso en el archivo CSV")
                ctx.exit(1)

            # Debe de estar fecha_elaboracion en el renglon
            if "fecha_elaboracion" not in renglon:
                click.echo("ERROR: Falta fecha_elaboracion en el archivo CSV")
                ctx.exit(1)

            # Si fecha_elaboracion es texto vacio, poner None
            fecha_elaboracion = None if renglon["fecha_elaboracion"] == "" else renglon["fecha_elaboracion"]

            # Debe de estar fecha_validacion en el renglon
            if "fecha_validacion" not in renglon:
                click.echo("ERROR: Falta fecha_validacion en el archivo CSV")
                ctx.exit(1)

            # Si fecha_validacion es texto vacio, poner None
            fecha_validacion = None if renglon["fecha_validacion"] == "" else renglon["fecha_validacion"]

            # Debe de estar fecha_autorizacion en el renglon
            if "fecha_autorizacion" not in renglon:
                click.echo("ERROR: Falta fecha_autorizacion en el archivo CSV")
                ctx.exit(1)

            # Si fecha_autorizacion es texto vacio, poner None
            fecha_autorizacion = None if renglon["fecha_autorizacion"] == "" else renglon["fecha_autorizacion"]

            # Debe estar estado en el renglon
            if "estado" not in renglon:
                click.echo("ERROR: Falta estado en el archivo CSV")
                ctx.exit(1)

            # Debe ser un estado valido
            estado = safe_string(renglon["estado"])
            if estado not in EstAcuerdo.ESTADOS:
                click.echo("Se omite el renglon por estado invalido")
                continue

            # Debe estar secretario en el renglon
            if "secretario" not in renglon:
                click.echo("ERROR: Falta secretario en el archivo CSV")
                ctx.exit(1)

            # Debe estar juez en el renglon
            if "juez" not in renglon:
                click.echo("ERROR: Falta juez en el archivo CSV")
                ctx.exit(1)

            # Insertar el equipo
            est_acuerdo = EstAcuerdo(
                distrito_nombre=safe_string(renglon["distrito_nombre"]),
                autoridad_descripcion=safe_string(renglon["autoridad_descripcion"]),
                folio=renglon["folio"],
                expediente=renglon["expediente"],
                numero_caso=renglon["numero_caso"],
                fecha_elaboracion=fecha_elaboracion,
                fecha_validacion=fecha_validacion,
                fecha_autorizacion=fecha_autorizacion,
                estado=estado,
                secretario=safe_string(renglon["secretario"], save_enie=True),
                juez=safe_string(renglon["juez"], save_enie=True),
            )
            est_acuerdo.save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")

    # Mensaje final
    click.echo(f"Se insertaron {contador} estadisticas acuerdos ")


cli.add_command(alimentar)
