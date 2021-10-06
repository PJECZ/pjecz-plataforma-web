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
            nombre = safe_string(row["nombre"])
            Rol(
                nombre=nombre,
                estatus=row["estatus"],
            ).save()
            click.echo(f"  {nombre}")
            contador += 1
    click.echo(f"  {contador} roles alimentados.")
