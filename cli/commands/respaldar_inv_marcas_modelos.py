"""
Respaldar Inventarios Marcas y Modelos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.inv_marcas.models import InvMarca


def respaldar_inv_marcas_modelos(salida: str = "inv_marcas_modelos.csv"):
    """Respaldar Inventarios Marcas y modelos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando inventarios marcas y modelos...")
    contador = 0
    inv_marcas = InvMarca.query.order_by(InvMarca.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "inv_modelo_id",
                "modelo_descripcion",
                "marca_nombre",
                "estatus",
            ]
        )
        for inv_marca in inv_marcas:
            for inv_modelo in inv_marca.inv_modelos:
                respaldo.writerow(
                    [
                        inv_modelo.id,
                        inv_modelo.descripcion,
                        inv_marca.nombre,
                        inv_modelo.estatus,
                    ]
                )
                contador += 1
                if contador % 100 == 0:
                    click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
