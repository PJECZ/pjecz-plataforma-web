"""
Alimentar usuarios
"""
from pathlib import Path
import csv
import click
from lib.pwgen import generar_contrasena

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

USUARIOS_CSV = "seed/usuarios_roles.csv"


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
            if "autoridad_clave" in row:
                autoridad_clave = row["autoridad_clave"]
                autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
                if autoridad is None:
                    click.echo(f"  AVISO: Falta la autoridad_clave {autoridad_clave}")
                    continue
            elif "autoridad_id" in row:
                autoridad_id = row["autoridad_id"]
                autoridad = Autoridad.query.get(autoridad_id)
                if autoridad is None:
                    click.echo(f"  AVISO: Falta la autoridad_id {autoridad_id}")
                    continue
            else:
                raise Exception("  ERROR: No tiene la columna autoridad_clave o autoridad_id")
            usuario_id = int(row["usuario_id"])
            if usuario_id != contador + 1:
                click.echo(f"  AVISO: usuario_id {usuario_id} no es consecutivo")
                continue
            Usuario(
                autoridad=autoridad,
                email=row["email"],
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
                curp=row["curp"],
                puesto=row["puesto"],
                telefono_celular=row["telefono_celular"],
                workspace=row["workspace"],
                estatus=row["estatus"],
                contrasena=pwd_context.hash(generar_contrasena()),
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} usuarios alimentados con contraseñas aleatorias.")
