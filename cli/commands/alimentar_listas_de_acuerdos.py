"""
Alimentar listas de acuerdos
"""
from datetime import datetime
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

LISTAS_DE_ACUERDOS_CSV = "seed/listas_de_acuerdos.csv"


def alimentar_listas_de_acuerdos():
    """ Alimentar Listas de Acuerdos """
    listas_de_acuerdos_csv = Path(LISTAS_DE_ACUERDOS_CSV)
    if not listas_de_acuerdos_csv.exists():
        click.echo(f"  NO se alimentaron listas de acuerdos porque no se encontró {LISTAS_DE_ACUERDOS_CSV}")
        return
    contador = 0
    with open(listas_de_acuerdos_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            datos = {
                "autoridad_id": int(row["autoridad_id"]),
                "archivo": row["archivo"].strip(),
                "fecha": datetime.strptime(row["fecha"], "%Y-%m-%d"),
                "descripcion": row["descripcion"].strip(),
                "url": row["url"].strip(),
            }
            ListaDeAcuerdo(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} listas de acuerdos...")
    click.echo(f"- {contador} listas de acuerdos alimentadas.")
