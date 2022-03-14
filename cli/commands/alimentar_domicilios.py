"""
Alimentar Domicilios
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.domicilios.models import Domicilio

DOMICILIOS_CSV = "seed/domicilios.csv"


def alimentar_domicilios():
    """Alimentar domicilios"""
    ruta = Path(DOMICILIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando domicilios...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            domicilio_id = int(row["domicilio_id"])
            if domicilio_id != contador + 1:
                click.echo(f"  AVISO: domicilio_id {domicilio_id} no es consecutivo")
                continue
            elementos = []
            calle = safe_string(row["calle"], max_len=256)
            num_ext = safe_string(row["num_ext"], max_len=24)
            num_int = safe_string(row["num_int"], max_len=24)
            colonia = safe_string(row["colonia"], max_len=256)
            municipio = safe_string(row["municipio"], max_len=64)
            estado = safe_string(row["estado"], max_len=64)
            cp = int(row["cp"])
            if calle:
                elementos.append(calle)
            if num_ext:
                elementos.append(f"#{num_ext}")
            if num_int:
                elementos.append("num_int")
            if colonia:
                elementos.append(colonia)
            if municipio:
                elementos.append(municipio)
            if estado:
                elementos.append(estado)
            if cp:
                elementos.append(f"C.P. {cp}")
            completo = " ".join(elementos)
            if completo.startswith("NO DEFINIDO"):
                completo = "NO DEFINIDO"
            Domicilio(
                estado=estado,
                municipio=municipio,
                calle=calle,
                num_ext=num_ext,
                num_int=num_int,
                colonia=colonia,
                cp=cp,
                completo=completo,
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} domicilios alimentados")
