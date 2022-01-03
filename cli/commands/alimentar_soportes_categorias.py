"""
Alimentar soportes categorias
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria

MATERIAS_TIPOS_JUICIOS_CSV = "seed/materias_tipos_juicios.csv"
