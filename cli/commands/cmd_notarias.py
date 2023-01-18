"""
Notarias

- alimentar: Insertar notarias a partir de un archivo CSV
"""
from datetime import datetime
from pathlib import Path

import csv
import click

from lib.pwgen import generar_contrasena
from lib.safe_string import safe_string

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.app import create_app
from plataforma_web.extensions import db, pwd_context

app = create_app()
db.app = app


@click.group()
def cli():
    """NOTARIAS"""


@click.command()
@click.argument("entrada_csv", type=str)
def alimentar(entrada_csv):
    """Alimentar a partir de un archivo CSV"""
    # Validar que exista el archivo CSV
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return

    click.echo("Alimentando usuarios que son notarias...")

    # Leer archivo CSV
    contador = 0
    with open(ruta, encoding="UTF8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:

            # Validar autoridad
            if "autoridad_id" in row:
                autoridad_id = row["autoridad_id"]
                autoridad = Autoridad.query.get(autoridad_id)
                if autoridad is None:
                    click.echo(f" AVISO: Falta la autoridad_id {autoridad_id}")
                    continue
            else:
                raise Exception(" ERROR: No tiene la columna autoridad_clave o autoridad_id")

            # Validar oficina
            if "oficina_id" in row:
                oficina_id = row["oficina_id"]
                oficina = Oficina.query.get(oficina_id)
                if oficina is None:
                    click.echo(f" AVISO: Falta la oficina_id {oficina_id}")
                    continue
            else:
                oficina = Oficina.query.get(1)  # Oficina NO DEFINIDO

            # Validar si existe email en la base de datos, se omite
            email = row["email"]
            if Usuario.query.filter_by(email=email).first() is not None:
                click.echo(f"AVISO: Ya existe un email registrado {email} en la base de datos, se omite")
                continue

            # Validar campos
            nombre = safe_string(row["nombre"])
            apellido_primero = safe_string(row["apellido_primero"])
            puesto = safe_string(row["puesto"])
            workspace = safe_string(row["workspace"])
            roles = row["roles"]

            # Insertar usuario
            usuario = Usuario(
                autoridad_id=autoridad_id,
                oficina_id=oficina_id,
                nombres=nombre,
                apellido_paterno=apellido_primero,
                email=email,
                puesto=puesto,
                workspace=workspace,
                contrasena=pwd_context.hash(generar_contrasena()),
                api_key="",
                api_key_expiracion=datetime(year=2000, month=1, day=1),
            )
            usuario.save()

            # Agregar Rol al usuario
            roles = Rol.query.filter_by(nombre=roles).first()
            if roles is None:
                click.echo(f"  AVISO: Falta el rol {roles}")
                continue
            UsuarioRol(
                usuario=usuario,
                rol=roles,
                descripcion=f"{usuario.email} en {roles.nombre}",
            ).save()

            # Contador de usuarios insertados
            contador += 1
            if contador % 50 == 0:
                click.echo(f" Van {contador}...")

    # Mensaje final
    click.echo(f"Se insertaron {contador} usuarios")


cli.add_command(alimentar)
