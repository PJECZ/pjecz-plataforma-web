"""
Respaldar Distritos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito


def respaldar_distritos(salida: str = "distritos.csv"):
    """Respaldar Distritos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando distritos...")
    contador = 0
    distritos = Distrito.query.order_by(Distrito.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["id", "nombre", "nombre_corto", "es_distrito_judicial", "estatus"])
        for distrito in distritos:
            respaldo.writerow(
                [
                    distrito.id,
                    distrito.nombre,
                    distrito.nombre_corto,
                    int(distrito.es_distrito_judicial),
                    distrito.estatus,
                ]
            )
            contador += 1
    click.echo(f"Respaldados {contador} distritos en {ruta.name}")
