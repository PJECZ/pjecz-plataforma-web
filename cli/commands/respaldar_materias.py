"""
Respaldar Materias
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.materias.models import Materia


def respaldar_materias(salida: str = "materias.csv"):
    """Respaldar Materias a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando materias...")
    contador = 0
    materias = Materia.query.order_by(Materia.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "materia_id",
                "nombre",
                "estatus",
            ]
        )
        for materia in materias:
            respaldo.writerow(
                [
                    materia.id,
                    materia.nombre,
                    materia.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
