"""
Respaldar Inventarios Categorias
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.inv_categorias.models import InvCategoria


def respaldar_inv_categorias(salida: str = "inv_categorias.csv"):
    """Respaldar Inventarios Categorias a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando inventarios categorias...")
    contador = 0
    inv_categorias = InvCategoria.query.order_by(InvCategoria.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "inv_categoria_id",
                "nombre",
                "estatus",
            ]
        )
        for inv_categoria in inv_categorias:
            respaldo.writerow(
                [
                    inv_categoria.id,
                    inv_categoria.nombre,
                    inv_categoria.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
