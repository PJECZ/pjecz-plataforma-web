"""
Rep Reportes

- elaborar: Elaborar reportes pendientes
- preparar_diarios: Preparar reportes diarios
"""
from datetime import datetime, timedelta, date
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.rep_reportes.models import RepReporte

app = create_app()
db.app = app


@click.group()
def cli():
    """Rep Reportes"""


@click.command()
def elaborar():
    """Elaborar reportes pendientes"""
    contador = 0
    reportes = RepReporte.query.filter(RepReporte.progreso == "PENDIENTE").filter(RepReporte.estatus == "A").all()
    for reporte in reportes:
        app.task_queue.enqueue(
            "plataforma_web.blueprints.reportes.tasks.elaborar",
            reporte_id=reporte.id,
        )
        click.echo(f"- Elaborar reporte {reporte.descripcion}")
        contador += 1
    if contador > 0:
        click.echo(f"Se lanzaron {contador} tareas para ejecutar en el fondo.")
    else:
        click.echo("No hay reportes pendientes.")


@click.command()
@click.option("--desde", default="", type=str, help="Fecha de inicio AAAA-MM-DD")
@click.option("--hasta", default="", type=str, help="Fecha de término AAAA-MM-DD")
def preparar_diarios(desde, hasta):
    """Preparar reportes diarios"""
    hoy = date.today()
    if desde != "":
        try:
            fecha = datetime.strptime(desde, "%Y-%m-%d").date()
        except ValueError:
            click.echo("ERROR: La fecha de inicio es incorrecta.")
            return
    else:
        fecha = hoy - timedelta(days=30)
        click.echo("Por defecto la fecha de inicio es " + str(fecha))
    if hasta != "":
        try:
            hasta_fecha = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            click.echo("AVISO: La fecha de término es incorrecta.")
            return
    else:
        hasta_fecha = hoy
    contador = 0
    delta = timedelta(days=1)
    while fecha <= hasta_fecha:
        click.echo(f"- Reporte para {fecha}")
        desde_tiempo = datetime(
            year=fecha.year,
            month=fecha.month,
            day=fecha.day,
            hour=0,
            minute=0,
            second=0,
        )
        hasta_tiempo = datetime(
            year=fecha.year,
            month=fecha.month,
            day=fecha.day,
            hour=23,
            minute=59,
            second=59,
        )
        programado_fecha = (hasta_tiempo + timedelta(days=1)).date()
        programado_tiempo = datetime(
            year=programado_fecha.year,
            month=programado_fecha.month,
            day=programado_fecha.day,
            hour=0,
            minute=0,
            second=0,
        )
        RepReporte(
            descripcion="Reporte diario",
            desde=desde_tiempo,
            hasta=hasta_tiempo,
            programado=programado_tiempo,
            progreso="PENDIENTE",
        ).save()
        fecha += delta
        contador += 1
    click.echo(f"Se prepararon {contador} reportes. Ahora puede elaborarlos.")


cli.add_command(elaborar)
cli.add_command(preparar_diarios)
