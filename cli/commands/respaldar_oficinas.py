"""
Respaldar Oficinas
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.oficinas.models import Oficina


def respaldar_oficinas(salida: str = "oficinas.csv"):
    """Respaldar Oficinas a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando oficinas...")
    contador = 0
    oficinas = Oficina.query.order_by(Oficina.id).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "oficina_id",
                "domicilio_id",
                "distrito_id",
                "descripcion",
                "descripcion_corta",
                "es_juridiccional",
                "apertura",
                "cierre",
                "limite_personas",
                "estatus",
            ]
        )
        for oficina in oficinas:
            respaldo.writerow(
                [
                    oficina.id,
                    oficina.domicilio_id,
                    oficina.distrito_id,
                    oficina.descripcion,
                    oficina.descripcion_corta,
                    1 if oficina.es_juridiccional else 0,
                    oficina.apertura,
                    oficina.cierre,
                    oficina.limite_personas,
                    oficina.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
