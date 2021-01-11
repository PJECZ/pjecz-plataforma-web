"""
Setup sirve para installar los comandos click
"""

import setuptools

setuptools.setup(
    name='plataforma_web',
    version='0.1',
    install_requires=[
        'click',
        'cryptography',
        'email-validator',
        'Flask',
        'Flask-Login',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Jinja2',
        'passlib',
        'PyMySQL',
        'SQLAlchemy',
        'SQLAlchemy-utils',
        'tabulate',
    ],
    entry_points="""
        [console_scripts]
        plataforma_web=cli.cli:cli
        """,
)
