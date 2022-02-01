"""
Clientes de Citas
"""
from pathlib import Path
import datetime

import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.cit_clientes.models import CITCliente
from plataforma_web.blueprints.cit_clientes.views import RENOVACION_CONTRASENA_DIAS

app = create_app()
db.app = app


@click.group()
def cli():
    """Citas Clientes"""

@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar Clientes de las Citas"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando clientes de las citas...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            curp = row["curp"]
            if len(curp) == 0:
                click.echo("!  CURP Vacía")
                continue
            cliente = CITCliente.query.filter(CITCliente.curp==curp).first()
            if cliente:
                click.echo(f"!  CURP repetida {curp}")
                continue
            CITCliente(
                id = int(row["id"]),
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
                email=row["email"],
                curp=row["curp"],
                telefono=row["telefono"],
                estatus = 'A' if int(row["estatus"]) == 1 else 'B',
                contrasena=row["contrasena"],
                hash=row["hash"],
                renovacion_fecha=datetime.date.today() + datetime.timedelta(days=RENOVACION_CONTRASENA_DIAS),
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} clientes de citas.")


@click.command()
@click.option("--output", default="citas_clientes.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return

    contador = 0
    clientes = CITCliente.query.filter_by(estatus="A").all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "id",
                "nombres",
                "apellido_paterno",
                "apellido_materno",
                "email",
                "domicilio_id",
                "curp",
                "telefono",
                "contrasena",
                "hash",
                "renovacion_fecha",
            ]
        )
        for cliente in clientes:
            respaldo.writerow(
                [
                    cliente.id,
                    cliente.nombres,
                    cliente.apellido_paterno,
                    cliente.apellido_materno,
                    cliente.email,
                    cliente.domicilio_id,
                    cliente.curp,
                    cliente.telefono,
                    cliente.contrasena,
                    cliente.hash,
                    cliente.renovacion_fecha,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)
