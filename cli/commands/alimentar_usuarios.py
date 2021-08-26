"""
Alimentar usuarios
"""
from pathlib import Path
import csv
import click
from lib.pwgen import generar_contrasena

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

USUARIOS_CSV = "seed/usuarios.csv"


def alimentar_usuarios():
    """Alimentar usuarios"""
    ruta = Path(USUARIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando usuarios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Usuario(
                rol_id=int(row["rol_id"]),
                autoridad_id=int(row["autoridad_id"]),
                email=row["email"],
                contrasena=pwd_context.hash(generar_contrasena()),
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
                telefono_celular=row["telefono_celular"],
                workspace=row["workspace"],
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"  {contador} usuarios alimentados con contraseñas aleatorias.")
