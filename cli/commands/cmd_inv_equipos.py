"""
Inventarios Equipos

- alimentar: Insertar equipos a partir de un archivo CSV
"""
import csv
from datetime import datetime
from pathlib import Path

import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_modelos.models import InvModelo

from plataforma_web.app import create_app
from plataforma_web.extensions import db

app = create_app()
db.app = app

INV_RED_ID = 3  # No Aplica


@click.group()
@click.pass_context
def cli(ctx):
    """Inventarios Equipos"""


@click.command()
@click.argument("archivo_csv", type=str)
@click.option("--descripcion", default=None, help="Descripcion")
@click.option("--fecha_fabricacion", default=None, help="Fecha de fabricacion")
@click.option("--inv_custodia_id", default=None, help="ID de la custodia")
@click.option("--inv_modelo_id", default=None, help="ID del modelo")
@click.option("--tipo", default=None, help="Tipo")
@click.pass_context
def alimentar(ctx, archivo_csv, descripcion, fecha_fabricacion, inv_custodia_id, inv_modelo_id, tipo):
    """Insertar equipos a partir de un archivo CSV"""

    # Validar que exista el archivo CSV
    archivo = Path(archivo_csv)
    if not archivo.exists():
        click.echo(f"ERROR: No existe el archivo {archivo_csv}")
        ctx.exit(1)

    # Validar descripcion
    if descripcion is not None:
        descripcion = safe_string(descripcion)

    # Validar fecha de fabricacion
    if fecha_fabricacion is not None:
        fecha_fabricacion = datetime.strptime(fecha_fabricacion, "%Y-%m-%d").date()
    else:
        fecha_fabricacion = datetime.now().date()

    # Validar custodia
    if inv_custodia_id is not None:
        if InvCustodia.query.get(inv_custodia_id) is None:
            click.echo(f"ERROR: No existe la custodia con ID {inv_custodia_id}")
            ctx.exit(1)

    # Validar modelo
    if inv_modelo_id is not None:
        if InvModelo.query.get(inv_modelo_id) is None:
            click.echo(f"ERROR: No existe el modelo con ID {inv_modelo_id}")
            ctx.exit(1)

    # Validar tipo
    if tipo is not None:
        if tipo not in InvEquipo.TIPOS:
            click.echo(f"ERROR: No existe el tipo {tipo}")
            ctx.exit(1)

    # Leer archivo CSV
    contador = 0
    with open(archivo_csv, "r", encoding="UTF8") as puntero:
        renglones = csv.DictReader(puntero)
        for renglon in renglones:

            # Si NO se tiene la descripcion, usar la del renglon
            if descripcion is None:
                if "descripcion" in renglon:
                    descripcion = safe_string(renglon["descripcion"])
                else:
                    click.echo("ERROR: Falta la descripcion en el archivo CSV")
                    ctx.exit(1)

            # Si NO se tiene la fecha de fabricacion se usa la del renglon
            if fecha_fabricacion is None:
                if "fecha_fabricacion" in renglon:
                    fecha_fabricacion = datetime.strptime(renglon["fecha_fabricacion"], "%Y-%m-%d").date()
                else:
                    click.echo("ERROR: Falta fecha_fabricacion en el archivo CSV")
                    ctx.exit(1)

            # Si NO se tiene la custodia se usa la del renglon
            if inv_custodia_id is None:
                if "inv_custodia_id" in renglon:
                    inv_custodia_id = int(renglon["inv_custodia_id"])
                    if InvCustodia.query.get(inv_custodia_id) is None:
                        click.echo(f"No existe la custodia con ID {inv_custodia_id}")
                        ctx.exit(1)
                else:
                    click.echo("ERROR: Falta inv_custodia_id en el archivo CSV")
                    ctx.exit(1)

            # Si NO se tiene el modelo se usa el del renglon
            if inv_modelo_id is None:
                if "inv_modelo_id" in renglon:
                    inv_modelo_id = int(renglon["inv_modelo_id"])
                    if InvModelo.query.get(inv_modelo_id) is None:
                        click.echo(f"No existe el modelo con ID {inv_modelo_id}")
                        ctx.exit(1)
                else:
                    click.echo("ERROR: Falta inv_modelo_id en el archivo CSV")
                    ctx.exit(1)

            # Si NO se tiene el tipo se usa el del renglon
            if tipo is None:
                if "tipo" in renglon:
                    tipo = renglon["tipo"]
                    if tipo not in InvEquipo.TIPOS:
                        click.echo(f"No existe el tipo {tipo}")
                        ctx.exit(1)
                else:
                    click.echo("ERROR: Falta tipo en el archivo CSV")
                    ctx.exit(1)

            # Debe de estar el numero de serie en el renglon
            if "numero_serie" not in renglon:
                click.echo("ERROR: Falta numero_serie en el archivo CSV")
                ctx.exit(1)

            # Debe de estar el numero de inventario en el renglon
            if "numero_inventario" not in renglon:
                click.echo("ERROR: Falta numero_inventario en el archivo CSV")
                ctx.exit(1)

            # Validar que el numero de serie no exista en la base de datos
            numero_serie = renglon["numero_serie"]
            if InvEquipo.query.filter_by(numero_serie=numero_serie).first() is not None:
                click.echo(f"AVISO: Ya existe un equipo con numero de serie {numero_serie} en la base de datos, se omite")
                continue

            # Tomar el numero de inventario
            numero_inventario = safe_string(renglon["numero_inventario"])

            # Insertar el equipo
            inv_equipo = InvEquipo(
                inv_custodia_id=inv_custodia_id,
                inv_modelo_id=inv_modelo_id,
                inv_red_id=INV_RED_ID,
                fecha_fabricacion=fecha_fabricacion,
                tipo=tipo,
                descripcion=descripcion,
                numero_serie=numero_serie,
                numero_inventario=numero_inventario,
            )
            inv_equipo.save()
            contador += 1

    # Mensaje final
    click.echo(f"Se insertaron {contador} equipos")


cli.add_command(alimentar)
