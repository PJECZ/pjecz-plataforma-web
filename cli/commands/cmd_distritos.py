"""
Distritos

- normalizar: Normalizar el nombre y el nombre_corto con safe_string
"""
import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito

app = create_app()
db.app = app


@click.group()
def cli():
    """Distritos"""


@click.command()
@click.option("--test", is_flag=True, help="Solo mostrar los cambios que se harian.")
def normalizar(test):
    """Normalizar el nombre y el nombre_corto con safe_string"""
    contador = 0
    distritos = Distrito.query.order_by(Distrito.id).filter_by(estatus="A").all()
    for distrito in distritos:
        nombre_normalizado = safe_string(distrito.nombre, save_enie=True)
        nombre_corto_normalizado = safe_string(distrito.nombre_corto, save_enie=True)
        if distrito.nombre != nombre_normalizado or distrito.nombre_corto != nombre_corto_normalizado:
            distrito.nombre = nombre_normalizado
            distrito.nombre_corto = nombre_corto_normalizado
            click.echo(f"  {distrito.nombre} -> {nombre_normalizado}")
            click.echo(f"  {distrito.nombre_corto} -> {nombre_corto_normalizado}")
            if not test:
                distrito.save()
                contador = contador + 1
    click.echo(f"Se actualizaron {contador} de {len(distritos)} distritos.")


cli.add_command(normalizar)
