"""
Alimentar usuarios
"""
import random
import string
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

USUARIOS_CSV = "seed/distritos_autoridades_usuarios.csv"


def generar_contrasena(largo=16):
    """ Generar contraseña """
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    simbolos = string.punctuation
    todos = minusculas + mayusculas + digitos + simbolos
    temp = random.sample(todos, largo)
    return "".join(temp)


def alimentar_usuarios():
    """ Alimentar usuarios """
    usuarios_csv = Path(USUARIOS_CSV)
    if not usuarios_csv.exists():
        click.echo(f"  No se alimentaron usuarios porque no se encontró {USUARIOS_CSV}")
        return
    agregados = []
    duplicados = []
    invalidos = []
    cantidad_sin_email = 0
    with open(usuarios_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            email = row["email"].strip()
            if email == "":
                cantidad_sin_email += 1
                continue
            if email.find("@") == -1:
                email = email + "@pjecz.gob.mx"
            if email in agregados:
                duplicados.append(email)
                continue
            if row["rol"].strip() == "":
                invalidos.append(email)
                continue
            rol = Rol.query.filter_by(nombre=row["rol"].strip()).first()
            if rol is None:
                invalidos.append(email)
                continue
            contrasena = row["contrasena"].strip()
            if contrasena == "":
                contrasena = generar_contrasena()
            datos = {
                "nombres": row["nombres"].strip(),
                "apellido_paterno": row["apellido_paterno"].strip(),
                "apellido_materno": row["apellido_materno"].strip(),
                "email": email,
                "contrasena": pwd_context.hash(contrasena),
                "rol": rol,
                "workspace": row["workspace"].strip(),
            }
            Usuario(**datos).save()
            agregados.append(email)
    if cantidad_sin_email > 0:
        click.echo(f"  {cantidad_sin_email} usuarios omitidos porque no tienen e-mail.")
    if len(duplicados) > 0:
        click.echo(f"  {len(duplicados)} usuarios omitidos por duplicados.")
    if len(invalidos) > 0:
        click.echo(f"  {len(invalidos)} usuarios porque el rol es vacío o incorrecto.")
    click.echo(f"- {len(agregados)} usuarios alimentados.")
