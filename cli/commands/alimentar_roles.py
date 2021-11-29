"""
Alimentar roles
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.roles.models import Rol

ROLES_CSV = "seed/roles_permisos.csv"


def alimentar_roles():
    """Alimentar roles"""
    ruta = Path(ROLES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando roles...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_id = int(row["rol_id"])
            if rol_id != contador + 1:
                click.echo(f"  AVISO: rol_id {rol_id} no es consecutivo")
                continue
            Rol(
                nombre=safe_string(row["nombre"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
    click.echo(f"  {contador} roles alimentados.")
