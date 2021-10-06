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
            autoridad_clave = row["autoridad_clave"]
            autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
            if autoridad is None:
                click.echo(f"  Falta la autoridad {autoridad_clave}")
                continue
            Usuario(
                autoridad=autoridad,
                email=row["email"],
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
                curp=row["curp"],
                puesto=row["puesto"],
                estatus=row["estatus"],
                contrasena=pwd_context.hash(generar_contrasena()),
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} usuarios...")
    click.echo(f"  {contador} usuarios alimentados con contraseñas aleatorias.")
