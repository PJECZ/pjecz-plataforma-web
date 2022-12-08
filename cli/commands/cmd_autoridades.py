"""
Autoridades

- normalizar: Normalizar la descripcion y la descripcion_corta con safe_string
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
@click.option("--actualizar", is_flag=True, help="Actualizar la base de datos.", default=False)
def normalizar(actualizar):
    """Normalizar la descripcion y la descripcion_corta con safe_string"""
    if not actualizar:
        click.echo("Modo de prueba. No se guardaran los cambios. Use --actualizar False para guardar.")
    contador = 0
    autoridades = Autoridad.query.order_by(Autoridad.id).filter_by(estatus="A").all()
    for autoridad in autoridades:
        descripcion_normalizado = safe_string(autoridad.descripcion, save_enie=True)
        descripcion_corta_normalizado = safe_string(autoridad.descripcion_corta, save_enie=True)
        hay_cambios = False
        if autoridad.descripcion != descripcion_normalizado:
            autoridad.descripcion = descripcion_normalizado
            click.echo(f"  {autoridad.descripcion} -> {descripcion_normalizado}")
            hay_cambios = True
        if autoridad.descripcion_corta != descripcion_corta_normalizado:
            autoridad.descripcion_corta = descripcion_corta_normalizado
            click.echo(f"  {autoridad.descripcion_corta} -> {descripcion_corta_normalizado}")
            hay_cambios = True
        if hay_cambios and actualizar:
            autoridad.save()
            contador = contador + 1
    click.echo(f"Se actualizaron {contador} de {len(autoridades)} autoridades.")


cli.add_command(normalizar)
