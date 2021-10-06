"""
Alimentar autoridades
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

AUTORIDADES_CSV = "seed/autoridades.csv"


def alimentar_autoridades():
    """Alimentar autoridades"""
    ruta = Path(AUTORIDADES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando autoridades...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito_id = int(row["distrito_id"])
            distrito = Distrito.query.get(distrito_id)
            if distrito is None:
                click.echo(f"  Falta el distrito {str(distrito_id)}")
                continue
            Autoridad(
                distrito=distrito,
                clave=row["clave"],
                descripcion=row["descripcion"],
                descripcion_corta=row["descripcion_corta"],
                es_jurisdiccional=(row["es_jurisdiccional"] == "1"),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} autoridades...")
    click.echo(f"  {contador} autoridades alimentadas.")
