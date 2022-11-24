"""
Autoridades

- normalizar: Actualiza el nombre de las autoridades con safe_string
"""
import click

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad

app = create_app()
db.app = app


@click.group()
def cli():
    """Autoridades"""


@click.command()
@click.option("--test", default=True, type=bool, help="Modo de prueba")
def normalizar(test):
    """Actualiza el nombre de las autoridades con safe_string"""
    if test:
        click.echo("-MODO PRUEBA-")

    contador = 0
    autoridades = Autoridad.query.order_by(Autoridad.id).all()
    for autoridad in autoridades:
        nombre_autoridad_normalizado = safe_string(autoridad.descripcion_corta, save_n=True)
        if autoridad.descripcion_corta != nombre_autoridad_normalizado:
            if test:
                click.echo(f"{autoridad.id:3} : {autoridad.descripcion_corta} --> {nombre_autoridad_normalizado}")
            else:
                autoridad.descripcion_corta = nombre_autoridad_normalizado
                autoridad.save()
                contador = contador + 1

    click.echo(f"Se actualizaron {contador} de {len(autoridades)} registros. Se respeto la Ñ, pero se eliminaron acentos.")


cli.add_command(normalizar)
