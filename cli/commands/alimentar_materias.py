"""
Alimentar materias
"""
import click

from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio


def alimentar_materias():
    """Alimentar materias"""
    click.echo("Alimentando materias...")
    materia_no_definido = Materia(nombre="NO DEFINIDO").save()
    Materia(nombre="CIVIL").save()
    Materia(nombre="FAMILIAR").save()
    Materia(nombre="MERCANTIL").save()
    Materia(nombre="LETRADO").save()
    Materia(nombre="FAMILIAR ORAL").save()
    Materia(nombre="PENAL").save()
    click.echo("  7 materias alimentadas.")
    click.echo("Alimentando tipos de juicios...")
    MateriaTipoJuicio(materia=materia_no_definido, descripcion="NO DEFINIDO")
    click.echo("  1 tipo de juicio alimentados.")
