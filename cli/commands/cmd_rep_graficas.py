"""
Rep Graficas

- elaborar: Elaborar todas las gráficas activas
"""
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
    """Elaborar todas las gráficas activas"""
    rep_graficas = RepGrafica.query.filter_by(estatus="A").order_by(RepGrafica.id).all()
    if len(rep_graficas) == 0:
        click.echo("No hay gráficas activas.")
        return
    cantidad = 0
    for rep_grafica in rep_graficas:
        app.task_queue.enqueue(
            "plataforma_web.blueprints.rep_graficas.tasks.elaborar",
            rep_grafica_id=rep_grafica.id,
        )
        cantidad += 1
        click.echo(f"- Elaborando {rep_grafica.descripcion}")
    if cantidad > 0:
        click.echo(f"Se lanzaron {cantidad} tareas en el fondo.")
    else:
        click.echo("Nada por hacer.")


cli.add_command(elaborar)
