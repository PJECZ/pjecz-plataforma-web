"""
Base de datos

- inicializar
- alimentar
- reiniciar
- respaldar
"""
import os
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from cli.commands.alimentar_autoridades import alimentar_autoridades
from cli.commands.alimentar_autoridades_funcionarios import alimentar_autoridades_funcionarios
from cli.commands.alimentar_centros_trabajos import alimentar_centros_trabajos
from cli.commands.alimentar_distritos import alimentar_distritos
from cli.commands.alimentar_domicilios import alimentar_domicilios
from cli.commands.alimentar_funcionarios import alimentar_funcionarios
from cli.commands.alimentar_inv_categorias import alimentar_inv_categorias
from cli.commands.alimentar_inv_marcas_modelos import alimentar_inv_marcas_modelos
from cli.commands.alimentar_inv_redes import alimentar_inv_redes
from cli.commands.alimentar_materias import alimentar_materias
from cli.commands.alimentar_materias_tipos_juicios import alimentar_materias_tipos_juicios
from cli.commands.alimentar_modulos import alimentar_modulos
from cli.commands.alimentar_oficinas import alimentar_oficinas
from cli.commands.alimentar_peritos_tipos import alimentar_peritos_tipos
from cli.commands.alimentar_permisos import alimentar_permisos
from cli.commands.alimentar_roles import alimentar_roles
from cli.commands.alimentar_soportes_categorias import alimentar_soportes_categorias
from cli.commands.alimentar_usuarios import alimentar_usuarios
from cli.commands.alimentar_usuarios_roles import alimentar_usuarios_roles

from cli.commands.respaldar_autoridades import respaldar_autoridades
from cli.commands.respaldar_centros_trabajos import respaldar_centros_trabajos
from cli.commands.respaldar_distritos import respaldar_distritos
from cli.commands.respaldar_domicilios import respaldar_domicilios
from cli.commands.respaldar_funcionarios import respaldar_funcionarios
from cli.commands.respaldar_inv_categorias import respaldar_inv_categorias
from cli.commands.respaldar_inv_marcas_modelos import respaldar_inv_marcas_modelos
from cli.commands.respaldar_inv_redes import respaldar_inv_redes
from cli.commands.respaldar_materias_tipos_juicios import respaldar_materias_tipos_juicios
from cli.commands.respaldar_materias import respaldar_materias
from cli.commands.respaldar_modulos import respaldar_modulos
from cli.commands.respaldar_oficinas import respaldar_oficinas
from cli.commands.respaldar_peritos_tipos import respaldar_peritos_tipos
from cli.commands.respaldar_roles_permisos import respaldar_roles_permisos
from cli.commands.respaldar_soportes_categorias import respaldar_soportes_categorias
from cli.commands.respaldar_usuarios_roles import respaldar_usuarios_roles

app = create_app()
db.app = app

entorno_implementacion = os.environ.get("DEPLOYMENT_ENVIRONMENT", "develop").upper()


@click.group()
def cli():
    """Base de Datos"""


@click.command()
def inicializar():
    """Inicializar"""
    if entorno_implementacion == "PRODUCTION":
        click.echo("PROHIBIDO: No se inicializa porque este es el servidor de producción.")
        return
    db.drop_all()
    db.create_all()
    click.echo("Termina inicializar.")


@click.command()
def alimentar():
    """Alimentar"""
    if entorno_implementacion == "PRODUCTION":
        click.echo("PROHIBIDO: No se alimenta porque este es el servidor de producción.")
        return
    alimentar_materias()
    alimentar_materias_tipos_juicios()
    alimentar_modulos()
    alimentar_roles()
    alimentar_permisos()
    alimentar_distritos()
    alimentar_autoridades()
    alimentar_domicilios()
    alimentar_oficinas()
    alimentar_inv_categorias()
    alimentar_inv_marcas_modelos()
    alimentar_inv_redes()
    alimentar_usuarios()
    alimentar_usuarios_roles()
    alimentar_centros_trabajos()
    alimentar_funcionarios()
    alimentar_autoridades_funcionarios()
    alimentar_peritos_tipos()
    # alimentar_soportes_categorias()
    click.echo("Termina alimentar.")


@click.command()
@click.pass_context
def reiniciar(ctx):
    """Reiniciar ejecuta inicializar y alimentar"""
    ctx.invoke(inicializar)
    ctx.invoke(alimentar)


@click.command()
def respaldar():
    """Respaldar"""
    respaldar_autoridades()
    respaldar_centros_trabajos()
    respaldar_distritos()
    respaldar_domicilios()
    respaldar_funcionarios()
    respaldar_materias_tipos_juicios()
    respaldar_materias()
    respaldar_modulos()
    respaldar_roles_permisos()
    respaldar_usuarios_roles()
    respaldar_oficinas()
    respaldar_inv_categorias()
    respaldar_inv_marcas_modelos()
    respaldar_inv_redes()
    respaldar_peritos_tipos()
    respaldar_soportes_categorias()
    click.echo("Termina respaldar.")


cli.add_command(inicializar)
cli.add_command(alimentar)
cli.add_command(reiniciar)
cli.add_command(respaldar)
