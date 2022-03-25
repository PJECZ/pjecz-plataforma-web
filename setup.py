"""
Comandos Click para instalar con pip install --editable .
"""
from setuptools import setup


setup(
    name="plataforma_web",
    version="0.1",
    packages=["plataforma_web"],
    entry_points="""
        [console_scripts]
        plataforma_web=cli.cli:cli
    """,
)
