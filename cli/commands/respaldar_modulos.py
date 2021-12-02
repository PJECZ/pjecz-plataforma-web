"""
Respaldar Modulos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.modulos.models import Modulo


def respaldar_modulos(salida: str = "modulos.csv"):
    """Respaldar Modulos a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando módulos...")
    contador = 0
    modulos = Modulo.query.order_by(Modulo.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "modulo_id",
                "nombre",
                "nombre_corto",
                "icono",
                "ruta",
                "en_navegacion",
                "estatus",
            ]
        )
        for modulo in modulos:
            if modulo.en_navegacion:
                en_navegacion = "1"
            else:
                en_navegacion = ""
            respaldo.writerow(
                [
                    modulo.id,
                    modulo.nombre,
                    modulo.nombre_corto,
                    modulo.icono,
                    modulo.ruta,
                    en_navegacion,
                    modulo.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} módulos en {ruta.name}")
