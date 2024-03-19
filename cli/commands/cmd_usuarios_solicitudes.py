"""
Usuarios Solicitudes

- enviar_sms: Enviar SMS vía Twilio al celular del usuario
- eliminar_registros: Eliminar solicitudes de más de 24hrs que no fueron validadas
"""

import click
import sys
import os
from datetime import datetime, timedelta

from twilio.rest import Client

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_TEL_FROM = os.getenv("TWILIO_TEL_FROM", "")
VALIDACION_TELEFONO_PERSONAL_URL = os.getenv("VALIDACION_TELEFONO_PERSONAL_URL", "")


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
@click.argument("usuario_email", type=str)
def enviar_whatsapp(usuario_email):
    """Enviar Whatsapp vía Twilio al celular del usuario"""

    # Seleccionamos al usuario por su correo
    usuario = Usuario.query.filter_by(email=usuario_email).first()

    # Si el usuario no está activo, mandamos un error.
    if usuario.estatus != 'A':
        click.echo("ERROR: El usuario no está activo")
        sys.exit(1)

    # Si el usuario no tiene un teléfono celular personal, mandamos un error.
    if usuario.telefono_celular is None or usuario.telefono_celular == "":
        click.echo("ERROR: El usuario no tiene un teléfono celular personal.")
        sys.exit(1)

    # Validar que se tiene VALIDACION_TELEFONO_PERSONAL_URL
    if VALIDACION_TELEFONO_PERSONAL_URL == "":
        click.echo("ERROR: NO esta configurada la variable VALIDACION_TELEFONO_PERSONAL_URL.")
        sys.exit(1)

    # Validar que se tiene TWILIO_ACCOUNT_SID
    if TWILIO_ACCOUNT_SID == "":
        click.echo("ERROR: NO esta configurada la variable TWILIO_ACCOUNT_SID.")
        sys.exit(1)

    # Validar que se tiene TWILIO_AUTH_TOKEN
    if TWILIO_AUTH_TOKEN == "":
        click.echo("ERROR: NO esta configurada la variable TWILIO_AUTH_TOKEN.")
        sys.exit(1)

    # Validar que se tiene TWILIO_TEL_FROM
    if TWILIO_TEL_FROM == "":
        click.echo("ERROR: NO esta configurada la variable TWILIO_TEL_FROM.")
        sys.exit(1)

    # Creamos el SMS de twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Enviar mensaje
    try:
        client.messages.create(
            body="Prueba de mensaje de Whatsapp",
            from_=f"whatsapp:{TWILIO_TEL_FROM}",
            to=f"whatsapp:+52{usuario.telefono_celular}",
        )
    except Exception as e:
        click.echo(f"ERROR: No se envió el whatsapp a {usuario.telefono_celular} por error de Twilio. {e}")
        sys.exit(1)

    # Mensaje final
    click.echo(f"Mensaje de Whatsapp enviado al +52{usuario.telefono_celular}")


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
