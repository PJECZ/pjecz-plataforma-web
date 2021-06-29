"""
Alimentar materias
"""
import click

from plataforma_web.blueprints.materias.models import Materia


def alimentar_materias():
    """Alimentar materias"""
    Materia(nombre="NO DEFINIDO").save()
    Materia(nombre="CIVIL").save()
    Materia(nombre="FAMILIAR").save()
    Materia(nombre="MERCANTIL").save()
    Materia(nombre="LETRADO").save()
    Materia(nombre="FAMILIAR ORAL").save()
    Materia(nombre="PENAL").save()
    click.echo("  Materias alimentadas.")
