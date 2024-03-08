"""
Usuarios Solicitudes

- enviar_sms: Enviar sms vía twilio a un usuario
- eliminar_registros: Elimina registros no validados con más de 24hrs
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
    """Enviar sms a un usuario"""
    click.echo("Enviar sms a usuario...")

    # Buscar usuario
    usuario_solicitud = UsuarioSolicitud.query.join(Usuario).filter(Usuario.email==usuario_email).first()

    if usuario_solicitud is None:
        click.echo("Usuario no localizado")
        sys.exit(1)

    # Lanzar tarea en el fondo para enviar email de validación
    app.task_queue.enqueue(
        "plataforma_web.blueprints.usuarios_solicitudes.tasks.enviar_telefono_validacion",
        usuario_solicitud_id=usuario_solicitud.id,
    )

    # Respuesta
    click.echo(f"Mensaje sms enviado a +52{usuario_solicitud.telefono_celular}")


@click.command()
def eliminar_registros():
    """Eliminar registros caducos"""
    click.echo("Eliminar registros con más de 24hrs...")

    # Buscar usuario_solicitudes
    usuarios_solicitudes = UsuarioSolicitud.query.filter(or_(UsuarioSolicitud.validacion_email==False, UsuarioSolicitud.validacion_telefono_celular==False)).filter_by(estatus="A").all()

    # Bucle
    contador = 0
    for usuario_solicitud in usuarios_solicitudes:
        if usuario_solicitud.creado <= datetime.now() + timedelta(days=1):
            usuario_solicitud.delete()
            contador = contador + 1
    # mensaje final
    click.echo(f"Se eliminaron {contador} registros.")

cli.add_command(enviar_sms)
cli.add_command(eliminar_registros)
