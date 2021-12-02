"""
Respaldar Usuarios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.usuarios.models import Usuario


def respaldar_usuarios(salida: str = "usuarios_roles.csv"):
    """Respaldar Usuarios a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando usuarios...")
    contador = 0
    usuarios = Usuario.query.order_by(Usuario.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "usuario_id",
                "autoridad_clave",
                "email",
                "nombres",
                "apellido_paterno",
                "apellido_materno",
                "curp",
                "puesto",
                "telefono_celular",
                "workspace",
                "roles",
                "estatus",
            ]
        )
        for usuario in usuarios:
            roles_list = []
            for usuario_rol in usuario.usuarios_roles:
                if usuario_rol.estatus == "A":
                    roles_list.append(usuario_rol.rol.nombre)
            respaldo.writerow(
                [
                    usuario.id,
                    usuario.autoridad.clave,
                    usuario.email,
                    usuario.nombres,
                    usuario.apellido_paterno,
                    usuario.apellido_materno,
                    usuario.curp,
                    usuario.puesto,
                    usuario.telefono_celular,
                    usuario.workspace,
                    ",".join(roles_list),
                    usuario.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
