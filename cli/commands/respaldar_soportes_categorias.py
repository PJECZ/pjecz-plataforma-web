"""
Respaldar soportes categorias
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria


def respaldar_soportes_categorias(salida: str = "soportes_categorias.csv"):
    """Respaldar categorias de soportes a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando tipos de peritos...")
    contador = 0
    soportes_categorias = SoporteCategoria.query.order_by(SoporteCategoria.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "soporte_categoria_id",
                "nombre",
                "estatus",
            ]
        )
        for soporte_categoria in soportes_categorias:
            respaldo.writerow(
                [
                    soporte_categoria.id,
                    soporte_categoria.nombre,
                    soporte_categoria.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
