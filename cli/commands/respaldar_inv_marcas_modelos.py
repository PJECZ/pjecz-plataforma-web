"""
Respaldar Inventarios Marcas y Modelos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.inv_modelos.models import InvModelo


def respaldar_inv_marcas_modelos(salida: str = "inv_marcas_modelos.csv"):
    """Respaldar Inventarios Marcas y modelos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando inventarios marcas y modelos...")
    contador = 0
    inv_modelos = InvModelo.query.order_by(InvModelo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "inv_modelo_id",
                "inv_marca_id",
                "inv_marca_nombre",
                "inv_modelo_descripcion",
                "estatus",
            ]
        )
        for inv_modelo in inv_modelos:
            respaldo.writerow(
                [
                    inv_modelo.id,
                    inv_modelo.inv_marca_id,
                    inv_modelo.inv_marca.nombre,
                    inv_modelo.descripcion,
                    inv_modelo.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
