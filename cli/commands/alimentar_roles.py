"""
Alimentar roles
"""
import click

from plataforma_web.blueprints.roles.models import Rol


def alimentar_roles():
    """ Alimentar roles """
    click.echo('Alimentando Roles...')
    Rol.insert_roles()
