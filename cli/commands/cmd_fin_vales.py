"""
Financieros Vales

- solicitar: Solicitar un vale con firma electronica
- autorizar: Autorizar un vale con firma electronica
"""
import getpass
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.fin_vales.models import FinVale

app = create_app()
db.app = app


@click.group()
def cli():
    """Financieros Vales"""


@click.command()
@click.argument("fin_vale_id")
def solicitar(fin_vale_id):
    """Solicitar un vale"""

    # Validar vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        click.echo("No se encontró el vale")
        return
    if fin_vale.estatus != "A":
        click.echo("El vale esta eliminado")
        return
    if fin_vale.estado != "CREADO":
        click.echo("El vale no tiene el estado CREADO")
        return

    # Mostrar detalle del vale
    click.echo(f"Financieros Vales")
    click.echo()
    click.echo("Quien lo pidio")
    click.echo(f"  ID:            {fin_vale_id}")
    click.echo(f"  Estado:        {fin_vale.estado}")
    click.echo(f"  Tipo:          {fin_vale.tipo}")
    click.echo(f"  Justificacion: {fin_vale.justificacion}")
    click.echo(f"  Monto:         {fin_vale.monto}")
    click.echo(f"  Creado:        {fin_vale.creado}")
    click.echo()

    # Solicitar la contrasena
    click.echo("Quien va a solicitar")
    click.echo(f"  Nombre: {fin_vale.solicito_nombre}")
    click.echo(f"  e-mail: {fin_vale.solicito_email}")
    contrasena = getpass.getpass("  Contraseña del motor de firma: ")
    click.echo()

    # Poner tarea en el fondo
    app.task_queue.enqueue(
        "plataforma_web.blueprints.fin_vales.tasks.solicitar",
        fin_vale_id=fin_vale_id,
        contrasena=contrasena,
    )
    click.echo("Solicitar vale se está ejecutando en el fondo.")


@click.command()
@click.argument("fin_vale_id")
def autorizar(fin_vale_id):
    """Autorizar un vale"""

    # Validar vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        click.echo("No se encontró el vale")
        return
    if fin_vale.estatus != "A":
        click.echo("El vale esta eliminado")
        return
    if fin_vale.estado != "SOLICITADO":
        click.echo("El vale no tiene el estado SOLICITADO")
        return

    # Mostrar detalle del vale
    click.echo(f"Financieros Vales")
    click.echo()
    click.echo("Quien lo pidio")
    click.echo(f"  ID:            {fin_vale_id}")
    click.echo(f"  Estado:        {fin_vale.estado}")
    click.echo(f"  Tipo:          {fin_vale.tipo}")
    click.echo(f"  Justificacion: {fin_vale.justificacion}")
    click.echo(f"  Monto:         {fin_vale.monto}")
    click.echo(f"  Creado:        {fin_vale.creado}")
    click.echo()

    # Solicitar la contrasena
    click.echo("Quien va a autorizar")
    click.echo(f"  Nombre: {fin_vale.autorizo_nombre}")
    click.echo(f"  e-mail: {fin_vale.autorizo_email}")
    contrasena = getpass.getpass("  Contraseña del motor de firma: ")
    click.echo()

    # Poner tarea en el fondo
    app.task_queue.enqueue(
        "plataforma_web.blueprints.fin_vales.tasks.autorizar",
        fin_vale_id=fin_vale_id,
        contrasena=contrasena,
    )
    click.echo("Autorizar vale se está ejecutando en el fondo.")


cli.add_command(solicitar)
cli.add_command(autorizar)
