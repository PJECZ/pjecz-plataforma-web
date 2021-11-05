"""
Usuarios - Roles

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from lib.pwgen import generar_contrasena
from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db, pwd_context

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from cli.commands.respaldar_usuarios_roles import respaldar_usuarios_roles

app = create_app()
db.app = app


@click.group()
def cli():
    """Usuarios"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    rol_por_defecto = Rol.query.filter_by(nombre="SICGD INVOLUCRADO").first()
    if rol_por_defecto is None:
        click.echo(f"ERROR: No existe registro para el rol por defecto SICGD INVOLUCRADO.")
        return
    click.echo("Alimentando usuarios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Tomar valores
            try:
                nombres = row["nombres"]
                apellido_paterno = row["apellido_paterno"]
                apellido_materno = row["apellido_materno"]
                curp = safe_string(row["curp"])
                email = row["email"]
                puesto = row["puesto"]
                autoridad_clave = row["autoridad_clave"]
                roles = row["roles"]
            except KeyError:
                click.echo("ERROR: Hacen falta columnas en este archivo CSV.")
                return
            # Si no tiene email se salta
            if email == "":
                continue
            # Si el e-mail es de coahuila.gob.mx
            if email.endswith("coahuila.gob.mx"):
                workspace = "COAHUILA"
            else:
                workspace = "EXTERNO"
            # Tomar la clave de la autoridad, si no esta se salta
            if autoridad_clave == "":
                continue
            autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
            if autoridad is None:
                continue
            # Si no tiene roles, se le asigna el rol por defecto
            if roles == "":
                roles = [rol_por_defecto]
            else:
                # TODO: Separar roles, consultarlos y ponerlos en listado
                click.echo("AVISO: No estoy listo para insertar varios usuarios_roles.")
                continue
            # Si el CURP NO esta
            usuario = Usuario.query.filter_by(curp=curp).first()
            if usuario is None:
                # Se debe insertar el usuario
                usuario = Usuario(
                    autoridad=autoridad,
                    email=email,
                    nombres=nombres,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    curp=curp,
                    puesto=puesto,
                    telefono_celular="",
                    workspace=workspace,
                    estatus="A",
                    contrasena=pwd_context.hash(generar_contrasena()),
                )
                usuario.save()
                contador += 1
                # Y sus usuarios_roles
                for rol in roles:
                    UsuarioRol(
                        usuario=usuario,
                        rol=rol,
                        descripcion=f"{usuario.email} en {rol.nombre}",
                    ).save()
            else:
                # TODO: Debe actualizar el usuario
                click.echo(f"  El usuario {email} ya esta presente.")
                continue
    click.echo(f"{contador} usuarios alimentados.")


@click.command()
@click.option("--output", default="usuarios_roles.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    respaldar_usuarios_roles(output)


cli.add_command(alimentar)
cli.add_command(respaldar)
