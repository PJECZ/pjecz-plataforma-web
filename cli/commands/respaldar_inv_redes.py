"""
Respaldar Inventarios Redes
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.inv_redes.models import InvRed


def respaldar_inv_redes(salida: str = "inv_redes.csv"):
    """Respaldar Inventarios Redes a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando inventarios redes...")
    contador = 0
    inv_redes = InvRed.query.order_by(InvRed.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "inv_red_id",
                "nombre",
                "tipo",
                "estatus",
            ]
        )
        for inv_red in inv_redes:
            respaldo.writerow(
                [
                    inv_red.id,
                    inv_red.nombre,
                    inv_red.tipo,
                    inv_red.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
