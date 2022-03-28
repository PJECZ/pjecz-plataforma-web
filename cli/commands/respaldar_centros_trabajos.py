"""
Respaldar Centros de Trabajos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo


def respaldar_centros_trabajos(salida: str = "centros_trabajos.csv"):
    """Respaldar Centros de Trabajo a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando centros de trabajo...")
    contador = 0
    centros_trabajos = CentroTrabajo.query.order_by(CentroTrabajo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "centro_trabajo_id",
                "clave",
                "nombre",
                "distrito_id",
                "estatus",
            ]
        )
        for centro_trabajo in centros_trabajos:
            respaldo.writerow(
                [
                    centro_trabajo.id,
                    centro_trabajo.clave,
                    centro_trabajo.nombre,
                    centro_trabajo.distrito_id,
                    centro_trabajo.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
