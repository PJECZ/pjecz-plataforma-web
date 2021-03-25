"""
Alimentar autoridades
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.autoridades.models import Autoridad

AUTORIDADES_CSV = "seed/distritos_autoridades_usuarios.csv"


def alimentar_autoridades():
    """ Alimentar autoridades """
    autoridades_csv = Path(AUTORIDADES_CSV)
    if not autoridades_csv.exists():
        click.echo(f"- NO se alimentaron autoridades porque no se encontró {AUTORIDADES_CSV}")
        return
    agregados = []
    with open(autoridades_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito = Distrito.query.filter_by(nombre=row["distrito"].strip()).first()
            descripcion = row["autoridad"].strip()
            if f"{distrito.nombre}, {descripcion}" in agregados:
                click.echo(f"- Se omite la autoridad {distrito.nombre}, {descripcion} por estar duplicado.")
                continue
            datos = {
                "descripcion": descripcion,
                "distrito": distrito,
                "directorio_listas_de_acuerdos": row["directorio_listas_de_acuerdos"].strip(),
                "directorio_sentencias": row["directorio_sentencias"].strip(),
            }
            Autoridad(**datos).save()
            agregados.append(f"{distrito.nombre}, {descripcion}")
    click.echo(f"- {len(agregados)} autoridades alimentadas.")
