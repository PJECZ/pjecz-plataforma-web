"""
REPSVM

- alimentar: Alimentar desde un archivo CSV
- publicar: Cambiar es_publico de los agresores a verdadero o falso
- reiniciar_consecutivos: Reiniciar los consecutivos de los agresores
- respaldar: Respaldar los agresores a un archivo CSV
"""
import csv
from pathlib import Path

import click
from lib.safe_string import safe_clave, safe_string, safe_text, safe_url

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor

app = create_app()
db.app = app

TIPOS_JUZGADOS_CLAVES = {
    "ND": "NO DEFINIDO",
    "J-EVF": "JUZGADO ESPECIALIZADO EN VIOLENCIA FAMILIAR",
    "J-PEN": "JUZGADO DE PRIMERA INSTANCIA EN MATERIA PENAL",
}


@click.group()
def cli():
    """REPSVM"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV"""

    # Validar que el archivo CSV exista
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return

    # Consultar el distrito NO DEFINIDO
    distrito_no_definido = Distrito.query.filter_by(nombre="NO DEFINIDO").first()
    if distrito_no_definido is None:
        click.echo("AVISO: No se encontró el distrito NO DEFINIDO.")
        return

    # Consultar el consecutivo mas alto por distrito
    consecutivos = {}
    for distrito in Distrito.query.filter_by(estatus="A").all():
        repsvm_agresor = REPSVMAgresor.query.filter_by(distrito_id=distrito.id).order_by(REPSVMAgresor.consecutivo.desc()).first()
        if repsvm_agresor is None:
            consecutivos[distrito.id] = 0
        else:
            consecutivos[distrito.id] = repsvm_agresor.consecutivo

    # Bucle para leer el archivo CSV
    click.echo("Alimentando agresores...")
    contador = 0
    distrito = None
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:

            # Tomar el tipo de juzgado
            tipo_juzgado = "ND"
            if "tipo_juzgado" in row:
                tipo_juzgado = safe_string(row["tipo_juzgado"])
                if tipo_juzgado not in REPSVMAgresor.TIPOS_JUZGADOS:
                    click.echo(f"! SE OMITE porque no es valido el tipo de juzgado {tipo_juzgado}")
                    continue

            # Tomar el tipo de sentencia
            tipo_sentencia = "ND"
            if "tipo_sentencia" in row:
                tipo_sentencia = safe_string(row["tipo_sentencia"])
                if tipo_sentencia not in REPSVMAgresor.TIPOS_SENTENCIAS:
                    click.echo(f"! SE OMITE porque no es valido el tipo de sentencia {tipo_sentencia}")
                    continue

            # Consultar el distrito
            distrito = distrito_no_definido
            if "distrito_id" in row:
                distrito = Distrito.query.get(int(row["distrito_id"]))
                if distrito is None:
                    click.echo(f"AVISO: No se encontró el distrito {row['distrito_id']}.")
                    continue

            # Si tiene es_publico, determinar el consecutivo y si es publico
            consecutivo = 0
            es_publico = False
            if "es_publico" in row:
                if distrito.id not in consecutivos:
                    click.echo(f"! SE OMITE porque no existe el ID distrito {distrito.id}")
                    continue
                consecutivos[distrito.id] += 1
                consecutivo = consecutivos[distrito.id]
                es_publico = row["es_publico"].strip().lower() == "si"

            # Insertar agresor
            REPSVMAgresor(
                distrito=distrito,
                consecutivo=consecutivo,
                delito_generico=safe_string(row["delito_generico"], save_enie=True),
                delito_especifico=safe_string(row["delito_especifico"], save_enie=True),
                es_publico=es_publico,
                nombre=safe_string(row["nombre"], save_enie=True),
                numero_causa=safe_string(row["numero_causa"]),
                pena_impuesta=safe_string(row["pena_impuesta"], save_enie=True),
                observaciones=safe_text(row["observaciones"]),
                sentencia_url=safe_url(row["sentencia_url"]),
                tipo_juzgado=tipo_juzgado,
                tipo_sentencia=tipo_sentencia,
            ).save()

            # Incrementar contador
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")

    click.echo(f"{contador} alimentados.")


@click.command()
@click.option("--es_publico", default=True, type=bool, help="True o False")
@click.option("--repsvm_agresor_id", default=None, type=int, help="ID del agresor")
def publicar(es_publico, repsvm_agresor_id):
    """Cambiar es_publico de los agresores a verdadero o falso"""

    # Si se especifica el ID del agresor
    if repsvm_agresor_id is not None:
        repsvm_agresor = REPSVMAgresor.query.get(repsvm_agresor_id)
        if repsvm_agresor is None:
            click.echo(f"! No existe el agresor {repsvm_agresor_id}")
            return
        repsvm_agresor.es_publico = es_publico
        if es_publico is False:
            repsvm_agresor.consecutivo = 0
        repsvm_agresor.save()
        click.echo(f"Se cambió es_publico de {repsvm_agresor_id} a {es_publico}")
        return

    # Consultar el consecutivo mas alto por distrito
    consecutivos = {}
    for distrito in Distrito.query.filter_by(estatus="A").all():
        repsvm_agresor = REPSVMAgresor.query.filter_by(distrito_id=distrito.id).order_by(REPSVMAgresor.consecutivo.desc()).first()
        if repsvm_agresor is None:
            consecutivos[distrito.id] = 0
        else:
            consecutivos[distrito.id] = repsvm_agresor.consecutivo

    # Bucle por todos los agresores
    contador = 0
    distrito_id = None
    for repsvm_agresor in REPSVMAgresor.query.filter_by(estatus="A").order_by(REPSVMAgresor.distrito_id, REPSVMAgresor.nombre):

        # Si es el primer registro o si cambia el distrito
        if distrito_id != repsvm_agresor.distrito_id:
            distrito_id = repsvm_agresor.distrito_id

        # Cambiar es_publico
        repsvm_agresor.es_publico = es_publico

        # Si es_publico es verdadero, incrementar el consecutivo y asignarlo
        if es_publico:
            consecutivos[distrito_id] += 1
            repsvm_agresor.consecutivo = consecutivos[distrito_id]
        else:
            repsvm_agresor.consecutivo = 0  # De lo contrario, ponerlo en cero

        # Guardar
        repsvm_agresor.save()

        # Incrementar contador
        contador += 1
        if contador % 100 == 0:
            click.echo(f"  Van {contador}...")

    click.echo(f"Se cambiaron {contador} agresores con es_publico a {es_publico}")


@click.command()
@click.option("--distrito_id", default=None, type=int, help="ID del Distrito")
@click.option("--output", default="repsvm.csv", type=str, help="Archivo CSV a escribir")
def respaldar(distrito_id, output):
    """Respaldar los agresores a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    contador = 0
    agresores = REPSVMAgresor.query.filter_by(estatus="A")
    if distrito_id is not None:
        agresores = agresores.filter(REPSVMAgresor.distrito_id == distrito_id)
        click.echo(f"Respaldando los agresores de REPSVM del distrito ID {distrito_id}...")
    else:
        click.echo("Respaldando TODOS los agresores de REPSVM...")
    agresores = agresores.order_by(REPSVMAgresor.distrito_id, REPSVMAgresor.consecutivo).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        encabezados = [
            "id",
            "distrito_id",
            "distrito_nombre_corto",
            "consecutivo",
            "nombre",
            "delito_generico",
            "delito_especifico",
            "numero_causa",
            "pena_impuesta",
            "observaciones",
            "tipo_juzgado",
            "tipo_sentencia",
            "sentencia_url",
        ]
        respaldo.writerow(encabezados)
        for agresor in agresores:
            fila = [
                agresor.id,
                agresor.distrito_id,
                agresor.distrito.nombre_corto,
                agresor.consecutivo,
                agresor.nombre,
                agresor.delito_generico,
                agresor.delito_especifico,
                agresor.numero_causa,
                agresor.pena_impuesta,
                agresor.observaciones,
                agresor.tipo_juzgado,
                agresor.tipo_sentencia,
                agresor.sentencia_url,
            ]
            respaldo.writerow(fila)
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} agresores en {ruta.name}")


@click.command()
@click.option("--distrito_id", default=None, type=int, help="ID del Distrito")
def reiniciar(distrito_id):
    """Reiniciar los consecutivos de los agresores"""
    distritos = []

    # Si se especifica el ID del distrito
    if distrito_id is not None:
        distrito = Distrito.query.get(distrito_id)
        if distrito is None:
            click.echo(f"! No existe el distrito {distrito_id}")
            return
        distritos.append(distrito)
    else:
        distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.id).all()

    # Bucle en todos los distritos
    contador = 0
    for distrito in distritos:
        click.echo(f"  {repr(distrito)}...")
        # Iniciar en cero
        consecutivo = 0
        # Bucle en todos los agresores del distrito ordenados por nombre
        for agresor in REPSVMAgresor.query.filter(REPSVMAgresor.distrito == distrito).filter_by(estatus="A").order_by(REPSVMAgresor.nombre).all():
            # Incrementar el consecutivo
            consecutivo += 1
            # Actualizar el consecutivo
            agresor.consecutivo = consecutivo
            agresor.save()
            # Incrementar el contador
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")

    click.echo(f"Se reiniciaron los consecutivos de {contador} agresores")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(publicar)
cli.add_command(reiniciar)
