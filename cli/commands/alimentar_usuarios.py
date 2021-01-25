"""
Alimentar usuarios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import pwd_context

USUARIOS_CSV = 'seed/usuarios.csv'


def alimentar_usuarios():
    """ Alimentar usuarios """
    usuarios_csv = Path(USUARIOS_CSV)
    if usuarios_csv.exists():
        with open(usuarios_csv, encoding='utf8') as puntero:
            rows = csv.DictReader(puntero)
            for row in rows:
                datos = {
                    'nombres': row['nombres'].strip(),
                    'apellido_paterno': row['apellido_paterno'].strip(),
                    'apellido_materno': row['apellido_materno'].strip(),
                    'email': row['email'].strip(),
                    'contrasena': pwd_context.hash(row['contrasena'].strip()),
                    'rol': Rol.query.filter_by(nombre=row['rol'].strip()).first(),
                }
                Usuario(**datos).save()
        click.echo('Usuarios alimentados.')
    else:
        click.echo(f'ERROR: No se encontró {USUARIOS_CSV}')
