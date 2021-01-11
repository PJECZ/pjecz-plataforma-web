"""
Roles: reiniciar
"""
import click

from cli.commands.alimentar_roles import alimentar_roles


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def reiniciar():
    """ Reiniciar los roles """
    alimentar_roles()
    click.echo('Reinicializado.')


cli.add_command(reiniciar)
