"""
Base de datos: inicializar, alimentar y reiniciar
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from cli.commands.alimentar_roles import alimentar_roles
from cli.commands.alimentar_usuarios import alimentar_usuarios

app = create_app()
db.app = app


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def inicializar():
    """ Inicializar """
    db.drop_all()
    db.create_all()
    click.echo('Inicializado.')


@click.command()
def alimentar():
    """ Alimentar """
    alimentar_roles()
    alimentar_usuarios()
    click.echo('Alimentado.')


@click.command()
@click.pass_context
def reiniciar(ctx):
    """ Reiniciar ejecuta inicializar y alimentar """
    ctx.invoke(inicializar)
    ctx.invoke(alimentar)


cli.add_command(inicializar)
cli.add_command(alimentar)
cli.add_command(reiniciar)
