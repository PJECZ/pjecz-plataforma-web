"""
Alimentar soportes categorias
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.roles.models import Rol

SOPORTES_CATEGORIAS_CSV = "seed/soportes_categorias.csv"


def alimentar_soportes_categorias():
    """Alimentar categorias de soportes"""
    ruta = Path(SOPORTES_CATEGORIAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando categorias de soportes...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            soporte_categoria_id = int(row["soporte_categoria_id"])
            if soporte_categoria_id != contador + 1:
                click.echo(f"  AVISO: soporte_categoria_id {soporte_categoria_id} no es consecutivo")
                continue
            # Validar Rol
            if "rol_id" in row:
                rol_id = row["rol_id"]
                rol = Rol.query.get(rol_id)
                if rol is None:
                    click.echo(f"  AVISO: Falta la rol_id {rol_id}")
                    continue
            else:
                rol = Rol.query.get(2)  # Rol SOPORTE TECNICO
            SoporteCategoria(
                nombre=safe_string(row["nombre"], save_enie=True),
                estatus=row["estatus"],
                rol=rol,
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} categorias alimentadas.")
