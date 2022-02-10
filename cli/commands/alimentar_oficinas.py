"""
Alimentar Oficinas
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.oficinas.models import Oficina

OFICINAS_CSV = "seed/oficinas.csv"


def alimentar_oficinas():
    """Alimentar oficinas"""
    ruta = Path(OFICINAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando oficinas...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            oficina_id = int(row["oficina_id"])
            if oficina_id != contador + 1:
                click.echo(f"  AVISO: oficina_id {oficina_id} no es consecutivo")
                continue
            Oficina(
                domicilio_id=int(row["domicilio_id"]),
                distrito_id=int(row["distrito_id"]),
                clave=safe_string(row["clave"]),
                descripcion=safe_string(row["descripcion"], max_len=512),
                descripcion_corta=safe_string(row["descripcion_corta"], max_len=64),
                es_jurisdiccional=bool(row["es_jurisdiccional"]),
                apertura=datetime.strptime(row["apertura"], "%H:%M:%S"),
                cierre=datetime.strptime(row["cierre"], "%H:%M:%S"),
                limite_personas=int(row["limite_personas"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} oficinas alimentados")
