"""
Alimentar soportes categorias
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria

SOPORTES_CATEGORIAS_CSV = "seed/soportes_categorias.csv"


def alimentar_soportes_categorias():
    """Alimentar soportes categorias"""
