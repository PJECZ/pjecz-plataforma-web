"""
Respaldar Domicilios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.domicilios.models import Domicilio


def respaldar_domicilios(salida: str = "domicilios.csv"):
    """Respaldar Domicilios a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando domicilios...")
    contador = 0
    domicilios = Domicilio.query.order_by(Domicilio.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "domicilio_id",
                "estado",
                "municipio",
                "calle",
                "num_ext",
                "num_int",
                "colonia",
                "cp",
                "numeracion_telefonica",
                "estatus",
            ]
        )
        for domicilio in domicilios:
            respaldo.writerow(
                [
                    domicilio.id,
                    domicilio.estado,
                    domicilio.municipio,
                    domicilio.calle,
                    domicilio.num_ext,
                    domicilio.num_int,
                    domicilio.colonia,
                    domicilio.cp,
                    domicilio.numeracion_telefonica,
                    domicilio.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
