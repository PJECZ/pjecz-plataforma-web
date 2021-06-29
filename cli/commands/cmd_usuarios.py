"""
Usuarios

- alimentar: Alimentar la tabla insertando registros desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
- nueva_contrasena: Cambiar contraseña de un usuario
"""
from pathlib import Path
import csv
import click
from lib.pwgen import generar_contrasena

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

app = create_app()
db.app = app


@click.group()
def cli():
    """Usuarios"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar la tabla insertando registros desde un archivo CSV"""
    ruta = Path(entrada_csv)
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
            ).save()
            contador += 1
    click.echo(f"{contador} usuarios alimentados.")


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando usuarios...")
    contador = 0
    usuarios = Usuario.query.order_by(Usuario.id).all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(
            [
                "id",
                "rol_id",
                "autoridad_id",
                "email",
                "nombres",
                "apellido_paterno",
                "apellido_materno",
                "telefono_celular",
                "workspace",
            ]
        )
        for usuario in usuarios:
            escritor.writerow(
                [
                    usuario.id,
                    usuario.rol_id,
                    usuario.autoridad_id,
                    usuario.email,
                    usuario.nombres,
                    usuario.apellido_paterno,
                    usuario.apellido_materno,
                    usuario.telefono_celular,
                    usuario.workspace,
                ]
            )
            contador += 1
    click.echo(f"Respaldadas {contador} usuarios.")


@click.command()
@click.argument("email", type=str)
def nueva_contrasena(email):
    """Cambiar contraseña de un usuario"""
    usuario = Usuario.find_by_identity(email)
    if usuario is None:
        click.echo(f"No existe el e-mail {email} en usuarios")
        return
    contrasena_1 = input("Contraseña: ")
    contrasena_2 = input("De nuevo la misma contraseña: ")
    if contrasena_1 != contrasena_2:
        click.echo("No son iguales las contraseñas. Por favor intente de nuevo.")
        return
    usuario.contrasena = pwd_context.hash(contrasena_1.strip())
    usuario.save()
    click.echo(f"Se ha cambiado la contraseña de {email} en usuarios")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(nueva_contrasena)
