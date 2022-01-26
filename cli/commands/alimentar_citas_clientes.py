"""
Alimentar usuarios
"""
from pathlib import Path
import datetime

import csv
import click

from plataforma_web.blueprints.cit_clientes.models import CITCliente
from plataforma_web.blueprints.cit_clientes.views import RENOVACION_CONTRASENA_DIAS

CSV = "seed/citas_clientes.csv"


def alimentar_citas_clientes():
    """Alimentar Clientes de las Citas"""
    ruta = Path(CSV)
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
                email=row["email"],
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
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
