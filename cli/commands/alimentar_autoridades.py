"""
Alimentar autoridades
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.autoridades.models import Autoridad

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
            Autoridad(
                distrito_id=int(row["distrito_id"]),
                materia_id=int(row["materia_id"]),
                descripcion=row["descripcion"],
                descripcion_corta=row["descripcion_corta"],
                clave=row["clave"],
                es_jurisdiccional=(row["es_jurisdiccional"] == "1"),
                es_notaria=(row["es_notaria"] == "1"),
                organo_jurisdiccional=row["organo_jurisdiccional"],
                directorio_edictos=row["directorio_edictos"],
                directorio_glosas=row["directorio_glosas"],
                directorio_listas_de_acuerdos=row["directorio_listas_de_acuerdos"],
                directorio_sentencias=row["directorio_sentencias"],
                audiencia_categoria=row["audiencia_categoria"],
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"  {contador} autoridades alimentadas.")
