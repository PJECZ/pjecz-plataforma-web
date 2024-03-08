"""
Usuarios Solicitudes

- enviar_sms: Enviar SMS vía Twilio al celular del usuario
- eliminar_registros: Eliminar solicitudes de más de 24hrs que no fueron validadas
"""

import click
import sys
from datetime import datetime, timedelta

from sqlalchemy import or_

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud

app = create_app()
db.app = app


@click.group()
def cli():
    """Usuario Solicitudes"""


@click.command()
@click.argument("usuario_email", type=str)
def enviar_sms(usuario_email):
    """Enviar SMS vía Twilio al celular del usuario"""

    # Consultar solicitudes activas del usuario dado
    usuario_solicitud = UsuarioSolicitud.query.join(Usuario).filter(Usuario.email == usuario_email).filter(UsuarioSolicitud.estatus == "A").first()

    # Si la consulta no arroja resultados
    if usuario_solicitud is None:
        click.echo(f"ERROR: El usuario {usuario_email} no tiene solicitudes activas. Nada que hacer.")
        sys.exit(1)

    # Lanzar la tarea en el fondo para enviar SMS de validación
    click.echo("Lanzando la tarea en el fondo para enviar SMS de validación...")
    app.task_queue.enqueue(
        "plataforma_web.blueprints.usuarios_solicitudes.tasks.enviar_sms_validacion",
        usuario_solicitud_id=usuario_solicitud.id,
    )

    # Mensaje final
    click.echo(f"Mensaje SMS de validación enviado a +52{usuario_solicitud.telefono_celular}")


@click.command()
def eliminar_solicitudes_no_validadas():
    """Eliminar solicitudes de más de 24hrs que no fueron validadas"""
    click.echo("Eliminar solicitudes de más de 24hrs que no fueron validadas...")

    # Consultar solicitudes activas
    usuarios_solicitudes = UsuarioSolicitud.query.filter_by(estatus="A").all()

    # Si la consulta no arroja resultados
    if usuarios_solicitudes is None:
        click.echo("AVISO: No hay solicitudes activas. Nada que hacer.")
        sys.exit(0)

    # Bucle por cada solicitud
    contador = 0
    for usuario_solicitud in usuarios_solicitudes:
        if usuario_solicitud.creado <= datetime.now() + timedelta(days=1):
            usuario_solicitud.delete()
            contador = contador + 1

    # Mensaje final
    click.echo(f"Se eliminaron {contador} solicitudes de más de 24hrs que no fueron validadas")


cli.add_command(enviar_sms)
cli.add_command(eliminar_solicitudes_no_validadas)
