"""
Alimentar abogados
"""
from datetime import datetime
from pathlib import Path
import csv
from unidecode import unidecode
import click

from plataforma_web.blueprints.abogados.models import Abogado

ABOGADOS_CSV = "seed/abogados.csv"


def alimentar_abogados():
    """ Alimentar abogados """
    abogados_csv = Path(ABOGADOS_CSV)
    if not abogados_csv.exists():
        click.echo(f"NO se alimentaron abogados porque no se encontró {ABOGADOS_CSV}")
        return
    contador = 0
    with open(abogados_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            fecha_str = row["fecha"].strip()
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")  # Probar que toda la fecha sea correcta
            except ValueError as mensaje:
                try:
                    fecha = datetime.strptime(fecha_str[0:8] + "-01", "%Y-%m-%d")  # Probar año y mes correctos
                except ValueError as mensaje:
                    try:
                        fecha = datetime.strptime(fecha_str[0:4] + "-01-01", "%Y-%m-%d")  # Probar año correcto
                    except ValueError as mensaje:
                        click.echo(f"  Dato con error: {mensaje}")
            numero = row["numero"].strip()  # Hay datos como 000-Bis
            nombre = unidecode(row["nombre"].strip()).upper()  # Sin acentos y en mayúsculas
            libro = unidecode(row["libro"].strip()).upper()  # Sin acentos y en mayúsculas
            datos = {
                "numero": numero,
                "nombre": nombre,
                "libro": libro,
                "fecha": fecha,
            }
            Abogado(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} abogados...")
    click.echo(f"- {contador} abogados alimentados.")
