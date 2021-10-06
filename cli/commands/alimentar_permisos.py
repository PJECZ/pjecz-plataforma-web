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
    modulos = Modulo.query.filter_by(estatus="A").all()
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
                click.echo(f"  Falta el rol_id {str(rol_id)}")
                return
            for modulo in modulos:
                columna = modulo.nombre.lower()
                if columna not in row:
                    click.echo(f"  Falta la columna {columna}")
                    continue
                try:
                    nivel = int(row[columna])
                    if nivel < 0 or nivel > 3:
                        click.echo("  Nivel incorrecto.")
                        continue
                except ValueError:
                    click.echo("  Se omite un permiso por no ser un número entre 0 y 3")
                    continue
                if nivel == 0:
                    continue
                nombre = f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}"
                Permiso(
                    rol=rol,
                    modulo=modulo,
                    nombre=nombre,
                    nivel=nivel,
                ).save()
                click.echo(f"  {nombre}")
                contador += 1
    click.echo(f"  {contador} permisos alimentados.")
