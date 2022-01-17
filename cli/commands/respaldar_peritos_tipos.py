"""
Respaldar Peritos Tipos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo


def respaldar_peritos_tipos(salida: str = "peritos_tipos.csv"):
    """Respaldar Tipos de Peritos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando tipos de peritos...")
    contador = 0
    peritos_tipos = PeritoTipo.query.order_by(PeritoTipo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "perito_tipo_id",
                "nombre",
                "estatus",
            ]
        )
        for perito_tipo in peritos_tipos:
            respaldo.writerow(
                [
                    perito_tipo.id,
                    perito_tipo.nombre,
                    perito_tipo.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
