"""
Alimentar modulos
"""
import click

from plataforma_web.blueprints.modulos.models import Modulo


def alimentar_modulos():
    """Alimentar modulos"""
    click.echo("Alimentando módulos...")
    Modulo(nombre="ABOGADOS").save()
    Modulo(nombre="AUDIENCIAS").save()
    Modulo(nombre="AUTORIDADES").save()
    Modulo(nombre="DOCUMENTACIONES").save()
    Modulo(nombre="DISTRITOS").save()
    Modulo(nombre="EDICTOS").save()
    Modulo(nombre="GLOSAS").save()
    Modulo(nombre="LISTAS DE ACUERDOS").save()
    Modulo(nombre="MATERIAS").save()
    Modulo(nombre="MATERIAS TIPOS JUICIOS").save()
    Modulo(nombre="MODULOS").save()
    Modulo(nombre="PERITOS").save()
    Modulo(nombre="REPORTES").save()
    Modulo(nombre="SENTENCIAS").save()
    Modulo(nombre="TRANSCRIPCIONES").save()
    Modulo(nombre="UBICACIONES DE EXPEDIENTES").save()
    Modulo(nombre="USUARIOS").save()
    click.echo("  12 módulos alimentados.")
