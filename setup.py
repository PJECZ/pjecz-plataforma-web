"""
Setup sirve para installar los comandos click
"""

import setuptools

setuptools.setup(
    name="plataforma_web",
    version="0.1",
    install_requires=[
        "click",
        "cryptography",
        "email-validator",
        "Flask",
        "Flask-Login",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "google-cloud-storage",
        "Jinja2",
        "passlib",
        "psycopg2-binary",
        "PyMySQL",
        "SQLAlchemy",
        "SQLAlchemy-utils",
        "tabulate",
        "unidecode",
    ],
    entry_points="""
        [console_scripts]
        plataforma_web=cli.cli:cli
        """,
)
