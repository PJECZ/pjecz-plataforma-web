"""
REPSVM

- Alimentar
"""
import csv
from pathlib import Path
import click
from lib.safe_string import safe_string, safe_text

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.materias_tipos_juzgados.models import MateriaTipoJuzgado
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor
from plataforma_web.blueprints.repsvm_delitos_especificos.models import REPSVMDelitoEspecifico
from plataforma_web.blueprints.repsvm_delitos_genericos.models import REPSVMDelitoGenerico
from plataforma_web.blueprints.repsvm_tipos_sentencias.models import REPSVMTipoSentencia

app = create_app()
db.app = app


@click.group()
def cli():
    """REPSVM"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    if MateriaTipoJuzgado.query.count() == 0:
        MateriaTipoJuzgado(
            materia=Materia.query.filter_by(nombre="NO DEFINIDO").first(),
            clave="ND",
            descripcion="NO DEFINIDO",
        ).save()
        click.echo("+ Se agrega el tipo de juzgado NO DEFINIDO")
    if REPSVMTipoSentencia.query.count() == 0:
        REPSVMTipoSentencia(nombre="NO DEFINIDO").save()
        click.echo("+ Se agrega el tipo de sentencia NO DEFINIDO")
    if REPSVMDelitoGenerico.query.count() == 0:
        REPSVMDelitoGenerico(nombre="NO DEFINIDO").save()
        click.echo("+ Se agrega el delito generico NO DEFINIDO")
    if REPSVMDelitoEspecifico.query.count() == 0:
        REPSVMDelitoEspecifico(
            repsvm_delito_generico=REPSVMDelitoGenerico.query.filter_by(nombre="NO DEFINIDO").first(),
            descripcion="NO DEFINIDO",
        ).save()
        click.echo("+ Se agrega el delito especifico NO DEFINIDO")
    click.echo("Alimentando ubicaciones de expedientes...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Distrito
            distrito_nombre = row["distrito"].strip()
            distrito = Distrito.query.filter_by(nombre=distrito_nombre).first()
            if distrito is None:
                click.echo(f"! SE OMITE porque no existe el distrito {distrito_nombre}")
                continue
            # Materia
            materia_nombre = safe_string(row["materia"])
            materia = Materia.query.filter_by(nombre=materia_nombre).first()
            if materia is None:
                click.echo(f"! SE OMITE porque no existe la materia {materia_nombre}")
                continue
            # Tipo de juzgado
            materia_tipo_juzgado_clave = safe_string(row["tipo_juzgado_clave"])
            materia_tipo_juzgado_descripcion = safe_string(row["tipo_juzgado_descripcion"])
            materia_tipo_juzgado = MateriaTipoJuzgado.query.filter_by(clave=materia_tipo_juzgado_clave).first()
            if materia_tipo_juzgado is None:
                materia_tipo_juzgado = MateriaTipoJuzgado(
                    materia=materia,
                    clave=materia_tipo_juzgado_clave,
                    descripcion=materia_tipo_juzgado_descripcion,
                ).save()
                click.echo(f"+ Se agrega el tipo de juzgado {materia_tipo_juzgado_clave}")
            # Tipo de sentencia
            repsvm_tipo_sentencia_nombre = safe_string(row["tipo_sentencia"])
            repsvm_tipo_sentencia = REPSVMTipoSentencia.query.filter_by(nombre=repsvm_tipo_sentencia_nombre).first()
            if repsvm_tipo_sentencia is None:
                repsvm_tipo_sentencia = REPSVMTipoSentencia(nombre=repsvm_tipo_sentencia_nombre).save()
                click.echo(f"+ Se agrega el tipo de sentencia {repsvm_tipo_sentencia_nombre}")
            # Delitos
            repsvm_delito_generico_nombre = safe_string(row["delito_generico"])
            repsvm_delito_generico = REPSVMDelitoGenerico.query.filter_by(nombre=repsvm_delito_generico_nombre).first()
            if repsvm_delito_generico is None:
                repsvm_delito_generico = REPSVMDelitoGenerico(nombre=repsvm_delito_generico_nombre).save()
                click.echo(f"+ Se agrega el delito generico {repsvm_delito_generico_nombre}")
            repsvm_delito_especifico_descripcion = safe_string(row["delito_especifico"])
            repsvm_delito_especifico = REPSVMDelitoEspecifico.query.filter(REPSVMDelitoEspecifico.repsvm_delito_generico == repsvm_delito_generico).filter_by(descripcion=repsvm_delito_especifico_descripcion).first()
            if repsvm_delito_especifico is None:
                repsvm_delito_especifico = REPSVMDelitoEspecifico(
                    repsvm_delito_generico=repsvm_delito_generico,
                    descripcion=repsvm_delito_especifico_descripcion,
                ).save()
                click.echo(f"+ Se agrega el delito especifico {repsvm_delito_especifico_descripcion}")
            # Insertar agresor
            REPSVMAgresor(
                distrito=distrito,
                materia_tipo_juzgado=materia_tipo_juzgado,
                repsvm_delito_especifico=repsvm_delito_especifico,
                repsvm_tipo_sentencia=repsvm_tipo_sentencia,
                nombre=safe_string(row["nombre"]),
                numero_causa=safe_string(row["numero_causa"]),
                pena_impuesta=safe_string(row["pena_impuesta"]),
                observaciones=safe_text(row["observaciones"], to_uppercase=True),
                sentencia_url=row["sentencia_url"].strip(),
            ).save()
            # Incrementar contador
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} alimentados.")


cli.add_command(alimentar)
