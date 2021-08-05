"""
Alimentar ubicación de expedientes
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente
from plataforma_web.blueprints.autoridades.models import Autoridad

UBICACION_EXPEDIENTES_CSV = "seed/ubicacion_expedientes.csv"


def alimentar_ubicacion_expedientes():
    """ Alimentar ubicación de expedientes """
    ubicacion_expedientes_csv = Path(UBICACION_EXPEDIENTES_CSV)
    if not ubicacion_expedientes_csv.exists():
        click.echo(f"NO se alimentaron autoridades porque no se encontró {UBICACION_EXPEDIENTES_CSV}")
        return
    contador = 0
    with open(ubicacion_expedientes_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            autoridad_str = row["autoridad"].strip()
            if autoridad_str == "":
                click.echo("  Sin autoridad...")
                continue
            autoridad = Autoridad.query.get(int(autoridad_str))
            if autoridad is False:
                click.echo(f"  No es válida la autoridad {row['autoridad']}...")
                continue
            ubicacion = row["ubicacion"].strip()
            if not ubicacion in UbicacionExpediente.UBICACIONES.keys():
                click.echo(f"  No es válida la ubicación {ubicacion}...")
                continue
            expediente = row["expediente"].strip()
            if expediente == "":
                click.echo("  Sin expediente...")
                continue
            datos = {
                "autoridad": autoridad,
                "expediente": expediente,
                "ubicacion": ubicacion,
            }
            UbicacionExpediente(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} ubicaciones de expedientes...")
    click.echo(f"  {contador} ubicaciones de expedientes alimentadas.")
