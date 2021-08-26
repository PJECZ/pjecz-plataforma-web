"""
Base de datos

- inicializar
- alimentar
- reiniciar
"""
import os
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from cli.commands.alimentar_autoridades import alimentar_autoridades
from cli.commands.alimentar_distritos import alimentar_distritos
from cli.commands.alimentar_materias import alimentar_materias
from cli.commands.alimentar_materias_tipos_juicios import alimentar_materias_tipos_juicios
from cli.commands.alimentar_modulos import alimentar_modulos
from cli.commands.alimentar_roles import alimentar_roles
from cli.commands.alimentar_usuarios import alimentar_usuarios

app = create_app()
db.app = app

entorno_implementacion = os.environ.get("DEPLOYMENT_ENVIRONMENT", "develop").upper()


@click.group()
def cli():
    """Base de Datos"""


@click.command()
def inicializar():
    """Inicializar"""
    if entorno_implementacion == "PRODUCTION":
        click.echo("PROHIBIDO: No se inicializa porque este es el servidor de producción.")
        return
    db.drop_all()
    db.create_all()
    click.echo("Inicializado.")


@click.command()
def alimentar():
    """Alimentar"""
    if entorno_implementacion == "PRODUCTION":
        click.echo("PROHIBIDO: No se alimenta porque este es el servidor de producción.")
        return
    alimentar_roles()
    alimentar_materias()
    alimentar_materias_tipos_juicios()
    alimentar_modulos()
    alimentar_distritos()
    alimentar_autoridades()
    alimentar_usuarios()
    click.echo("Alimentado.")


@click.command()
@click.pass_context
def reiniciar(ctx):
    """Reiniciar ejecuta inicializar y alimentar"""
    ctx.invoke(inicializar)
    ctx.invoke(alimentar)


cli.add_command(inicializar)
cli.add_command(alimentar)
cli.add_command(reiniciar)
