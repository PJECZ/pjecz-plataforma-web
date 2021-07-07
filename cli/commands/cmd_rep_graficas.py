"""
Rep Graficas

- elaborar: Elaborar reportes pendientes de las gráficas
"""
from datetime import datetime, timedelta, date
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.rep_graficas.models import RepGrafica

app = create_app()
db.app = app


@click.group()
def cli():
    """Rep Gráficas"""


@click.command()
def elaborar():
    """Elaborar reportes pendientes de las gráficas"""
    rep_graficas = RepGrafica.query.filter(RepGrafica.estatus == "A").order_by(RepGrafica.id).all()
    for rep_grafica in rep_graficas:
        click.echo(f"  Gráfica: {rep_grafica.descripcion}")
        for rep_reporte in rep_grafica.rep_reportes:
            click.echo(f"    Reporte: {rep_reporte.descripcion}")


cli.add_command(elaborar)
