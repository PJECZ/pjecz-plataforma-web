"""
Respaldar Roles-Permisos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.roles.models import Rol


def respaldar_roles_permisos(salida: str = "roles_permisos.csv"):
    """Respaldar Roles-Permisos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando roles...")
    contador = 0
    roles = Rol.query.order_by(Rol.id).all()
    modulos = Modulo.query.order_by(Modulo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        encabezados = [
            "rol_id",
            "nombre",
        ]
        for modulo in modulos:
            encabezados.append(modulo.nombre.lower())
        encabezados.append("estatus")
        respaldo = csv.writer(puntero)
        respaldo.writerow(encabezados)
        for rol in roles:
            renglon = [rol.id, rol.nombre]
            for modulo in modulos:
                permiso_str = ""
                for permiso in rol.permisos:
                    if permiso.modulo_id == modulo.id and permiso.estatus == "A":
                        permiso_str = str(permiso.nivel)
                renglon.append(permiso_str)
            renglon.append(rol.estatus)
            respaldo.writerow(renglon)
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
