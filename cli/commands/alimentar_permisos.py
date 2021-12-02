"""
Alimentar permisos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.roles.models import Rol

PERMISOS_CSV = "seed/roles_permisos.csv"


def alimentar_permisos():
    """Alimentar permisos"""
    ruta = Path(PERMISOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    modulos = Modulo.query.all()
    if len(modulos) == 0:
        click.echo("AVISO: Faltan de alimentar los modulos")
        return
    click.echo("Alimentando permisos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_id = int(row["rol_id"])
            rol = Rol.query.get(rol_id)
            if rol is None:
                click.echo(f"  ERROR: Falta el rol_id {rol_id}")
                return
            for modulo in modulos:
                columna = modulo.nombre.lower()
                if columna not in row:
                    click.echo(f"  AVISO: Falta la columna {columna}")
                    continue
                try:
                    if row[columna] == "":
                        continue
                    nivel = int(row[columna])
                    if nivel < 0 or nivel > 4:
                        click.echo(f"  AVISO: Nivel {nivel} es incorrecto.")
                        continue
                except ValueError:
                    click.echo("  AVISO: Se omite un permiso por no ser un número entre 0 y 3")
                    continue
                if nivel == 0:
                    continue
                Permiso(
                    rol=rol,
                    modulo=modulo,
                    nombre=f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}",
                    nivel=nivel,
                ).save()
                contador += 1
                if contador % 100 == 0:
                    click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} permisos alimentados.")
