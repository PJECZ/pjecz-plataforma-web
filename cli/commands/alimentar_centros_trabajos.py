"""
Alimentar centros de trabajos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo

CENTROS_TRABAJOS_CSV = "seed/centros_trabajos.csv"


def alimentar_centros_trabajos():
    """Alimentar distritos"""
    ruta = Path(CENTROS_TRABAJOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando centros de trabajos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            centro_trabajo_id = int(row["centro_trabajo_id"])
            if centro_trabajo_id != contador + 1:
                click.echo(f"  AVISO: centro_trabajo_id {centro_trabajo_id} no es consecutivo")
                continue
            CentroTrabajo(
                clave=row["clave"],
                nombre=row["nombre"],
                telefono=row["telefono"],
                distrito_id=int(row["distrito_id"]),
                domicilio_id=int(row["domicilio_id"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} centros de trabajos alimentados.")
