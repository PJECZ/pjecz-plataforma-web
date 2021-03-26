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
        click.echo(f"  NO se alimentaron autoridades porque no se encontró {AUTORIDADES_CSV}")
        return
    agregados = []
    duplicados = []
    cantidad_sin_clave = 0
    cantidad_activos = 0
    cantidad_inactivos = 0
    with open(autoridades_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            clave = row["clave"].strip()
            if clave == "":
                cantidad_sin_clave += 1
                continue
            if clave in agregados:
                duplicados.append(clave)
                continue
            distrito = Distrito.query.filter_by(nombre=row["distrito"].strip()).first()
            if distrito is None:
                continue
            descripcion = row["autoridad"].strip()
            if descripcion == "":
                continue
            email = row["email"].strip()
            if email == "":
                estatus = "B"
                cantidad_inactivos += 1
            else:
                estatus = "A"
                cantidad_activos += 1
            es_jurisdiccional = int(row["es_jurisdiccional"].strip()) == 1
            datos = {
                "descripcion": descripcion,
                "distrito": distrito,
                "clave": clave,
                "directorio_listas_de_acuerdos": row["directorio_listas_de_acuerdos"].strip(),
                "directorio_sentencias": row["directorio_sentencias"].strip(),
                "es_jurisdiccional": es_jurisdiccional,
                "estatus": estatus,
            }
            Autoridad(**datos).save()
            agregados.append(clave)
    if cantidad_sin_clave > 0:
        click.echo(f"  {cantidad_sin_clave} autoridades omitidas por no tener clave.")
    if len(duplicados) > 0:
        click.echo(f"  {len(duplicados)} autoridades omitidas por duplicados.")
    click.echo(f"- {len(agregados)} autoridades alimentadas: {cantidad_activos} activas, {cantidad_inactivos} inactivas.")
