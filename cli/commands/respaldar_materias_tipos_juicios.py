"""
Respaldar Materias-Tipos de Juicios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio


def respaldar_materias_tipos_juicios(salida: str = "materias_tipos_juicios.csv"):
    """Respaldar Materias-Tipos de Juicios a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando materias/tipos de juicios...")
    contador = 0
    materias_tipos_juicios = MateriaTipoJuicio.query.order_by(MateriaTipoJuicio.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "materia_id", "descripcion", "estatus"])
        for materia in materias_tipos_juicios:
            respaldo.writerow(
                [
                    materia.id,
                    materia.materia_id,
                    materia.descripcion,
                    materia.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} materias/tipos de juicios en {ruta.name}")
