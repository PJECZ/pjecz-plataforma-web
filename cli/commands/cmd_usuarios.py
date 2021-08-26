"""
Usuarios

- respaldar: Respaldar a un archivo CSV
- nueva_contrasena: Cambiar contraseña de un usuario
"""
from pathlib import Path
import csv
import click

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
@click.option("--output", default="usuarios.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando usuarios...")
    contador = 0
    usuarios = Usuario.query.order_by(Usuario.id).all()
    with open(ruta, "w") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
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
                "estatus",
            ]
        )
        for usuario in usuarios:
            respaldo.writerow(
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
                    usuario.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldadas {contador} en {ruta.name}")


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


cli.add_command(respaldar)
cli.add_command(nueva_contrasena)
