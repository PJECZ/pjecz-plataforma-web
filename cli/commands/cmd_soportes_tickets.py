"""
Soportes Tickets
"""

import re
from pathlib import Path

import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket

app = create_app()
db.app = app


@click.group()
def cli():
    """Soportes Tickets"""


@click.command()
@click.argument("desde", type=str)
@click.argument("hasta", type=str)
@click.option("--output", default="soportes_tickets.csv", type=str, help="Archivo CSV a escribir")
def respaldar(desde, hasta, output):
    """Respaldar Soportes Tickets a un archivo CSV"""
    # Validar el archivo CSV a escribir, que no exista
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {output} existe, no voy a sobreescribirlo.")
        return
    # Validar que el parametro desde sea YYYY-MM-DD
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", desde):
        click.echo(f"ERROR: {desde} no es una fecha valida (YYYY-MM-DD)")
        return
    # Validar que el parametro hasta sea YYYY-MM-DD
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", hasta):
        click.echo(f"ERROR: {hasta} no es una fecha valida (YYYY-MM-DD)")
        return
    # Validar que la fecha desde sea menor que la fecha hasta
    if desde > hasta:
        click.echo(f"ERROR: {desde} es mayor que {hasta}")
        return
    # Consultar soportes tickets
    click.echo("Respaldando soportes tickets...")
    contador = 0
    soportes_tickets = SoporteTicket.query.order_by(SoporteTicket.id)
    if desde:
        soportes_tickets = soportes_tickets.filter(SoporteTicket.creado >= f"{desde} 00:00:00")
    if hasta:
        soportes_tickets = soportes_tickets.filter(SoporteTicket.creado <= f"{hasta} 23:59:59")
    soportes_tickets = soportes_tickets.all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "Fecha",
                "Fecha de respuesta",
                "Usuario",
                "Soporte Técnico",
                "Descripción",
                "Solución",
                "Estado",
                "ID",
            ]
        )
        for soporte_ticket in soportes_tickets:
            # Reemplazar los avances de linea en descripciones y soluciones
            soporte_ticket_descripcion = soporte_ticket.descripcion.replace("\n", " ")
            soporte_ticket_soluciones = soporte_ticket.soluciones.replace("\n", " ")
            respaldo.writerow(
                [
                    soporte_ticket.creado.strftime("%Y-%m-%d %H:%M:%S"),
                    soporte_ticket.modificado.strftime("%Y-%m-%d %H:%M:%S"),
                    soporte_ticket.usuario.nombre,
                    soporte_ticket.funcionario.nombre,
                    soporte_ticket_descripcion,
                    soporte_ticket_soluciones,
                    soporte_ticket.estado,
                    soporte_ticket.id,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")


cli.add_command(respaldar)
