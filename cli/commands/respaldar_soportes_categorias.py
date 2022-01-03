"""
Respaldar soportes categorias
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria


def respaldar_soportes_categorias(salida: str = "soportes_categorias.csv"):
    """Respaldar Soportes Categorias a un archivo CSV"""
