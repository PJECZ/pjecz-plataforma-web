"""
Alimentar funcionarios
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.funcionarios.models import Funcionario

FUNCIONARIOS_CSV = "seed/funcionarios.csv"


def alimentar_funcionarios():
    """Alimentar funcionarios"""
    ruta = Path(FUNCIONARIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando funcionarios...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            funcionario_id = int(row["funcionario_id"])
            if funcionario_id != contador + 1:
                click.echo(f"  AVISO: funcionario_id {funcionario_id} no es consecutivo")
                continue
            Funcionario(
                nombres=safe_string(row["nombres"]),
                apellido_paterno=safe_string(row["apellido_paterno"]),
                apellido_materno=safe_string(row["apellido_materno"]),
                curp=safe_string(row["curp"]),
                email=row["email"],
                puesto=safe_string(row["puesto"]),
                en_funciones=(int(row["en_funciones"]) == 1),
                en_sentencias=(int(row["en_sentencias"]) == 1),
                en_soportes=(int(row["en_soportes"]) == 1),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} funcionarios alimentados")
