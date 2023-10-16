"""
Ubicación Expedientes

- actualizar: Actualizar ubicaciones de expedientes con la informacion de arc_documentos
- alimentar: Alimentar desde un archivo CSV con el nombre de la clave de la autoridad
- respaldar: Respaldar a un archivo CSV
- reiniciar: Elimina todas las ubicaciones de expedientes de una autoridad
"""
import re
from datetime import date
from pathlib import Path
import csv
import click

from lib.safe_string import safe_clave

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente

app = create_app()
db.app = app


@click.group()
def cli():
    """Ubicación Expedientes"""


@click.command()
@click.argument("autoridad_clave", type=str)
def actualizar(autoridad_clave):
    """Actualizar ubicaciones de expedientes con la informacion de arc_documentos"""

    # Validar autoridad
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave == "":
        click.echo("No es correcta la clave de la autoridad")
        return
    autoridad = Autoridad.query.filter(Autoridad.clave == autoridad_clave).first()
    if autoridad is None:
        click.echo(f"No existe la clave {autoridad_clave} en autoridades")
        return
    if autoridad.estatus != "A":
        click.echo(f"La autoridad {autoridad_clave} no está activa")
        return
    if not autoridad.es_jurisdiccional:
        click.echo(f"La autoridad {autoridad_clave} no es jurisdiccional")
        return
    if autoridad.es_extinto:
        click.echo(f"La autoridad {autoridad_clave} es extinta")
        return
    if autoridad.es_notaria:
        click.echo(f"La autoridad {autoridad_clave} es una notaría")
        return

    # Consultar arc_documentos de la autoridad y activos
    arc_documentos = ArcDocumento.query.filter_by(autoridad=autoridad).filter_by(estatus="A")
    if arc_documentos.count() == 0:
        click.echo(f"No hay arc_documentos para la autoridad {autoridad_clave}")
        return

    # Definir la base de datos para hacer operaciones por lotes
    database = db.session

    # Inicializar contadores
    contador_agregados = 0
    contador_actualizados = 0
    contador_duplicados_eliminados = 0

    # Bucle por cada arc_documento
    for arc_documento in arc_documentos.all():
        # Consultar en ubicaciones de expedientes, con la autoridad dada dicho expediente
        ubicaciones_expedientes = UbicacionExpediente.query
        ubicaciones_expedientes = ubicaciones_expedientes.filter_by(autoridad=autoridad)
        ubicaciones_expedientes = ubicaciones_expedientes.filter_by(expediente=arc_documento.expediente)
        ubicaciones_expedientes = ubicaciones_expedientes.filter_by(estatus="A")
        ubicaciones_expedientes = ubicaciones_expedientes.all()
        # Separar el primer resultado, porque puede haber mas de uno
        ubicacion_expediente = None
        if len(ubicaciones_expedientes) > 0:
            ubicacion_expediente = ubicaciones_expedientes[0]
            # Si hay mas de un resultado, dar de baja los demas
            if len(ubicaciones_expedientes) > 1:
                for ubicacion_expediente in ubicaciones_expedientes[1:]:
                    ubicacion_expediente.estatus = "B"
                    database.commit()
                    contador_duplicados_eliminados += 1
        # Si la ubicacion en Archivo es REMESA, entonces en UdE sera ARCHIVO
        la_ubicacion = arc_documento.ubicacion
        if la_ubicacion == "REMESA":
            la_ubicacion = "ARCHIVO"
        # Si no existe, crearlo
        if ubicacion_expediente is None:
            datos = {
                "autoridad": autoridad,
                "expediente": arc_documento.expediente,
                "ubicacion": la_ubicacion,
            }
            database.add(UbicacionExpediente(**datos))
            contador_agregados += 1
            # Cargar por lotes de 100
            if contador_agregados % 100 == 0:
                database.commit()
                click.echo(f"  Van {contador_agregados} agregados...")
        # Si existe, actualizarlo en caso de ubicacion sea diferente
        elif ubicacion_expediente.ubicacion != la_ubicacion:
            ubicacion_expediente.ubicacion = la_ubicacion
            database.commit()
            contador_actualizados += 1

    # Cargar el ultimo lote
    if contador_agregados % 100 != 0:
        database.commit()

    # Mostrar contadores
    click.echo(f"Actualizar ubicaciones de expedientes para {autoridad_clave} ha terminado")
    click.echo(f"  {contador_agregados} agregados")
    click.echo(f"  {contador_actualizados} actualizados")
    click.echo(f"  {contador_duplicados_eliminados} duplicados eliminados")


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV con el nombre de la clave de la autoridad"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    clave = ruta.name[: -len(ruta.suffix)]
    autoridad = Autoridad.query.filter(Autoridad.clave == clave).first()
    if autoridad is None:
        click.echo(f"AVISO: Con el nombre del archivo {ruta.name} no hay clave en autoridades.")
        return
    click.echo("Alimentando ubicaciones de expedientes...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Validar ubicación
            ubicacion = row["ubicacion"].strip()
            if not ubicacion in UbicacionExpediente.UBICACIONES.keys():
                click.echo("! Ubicación no válida")
                continue
            # Validar expediente
            try:
                if not row["expediente"] or row["expediente"].strip() == "":
                    click.echo("! Expediente vacio ")
                    continue
                elementos = re.sub(r"[^0-9]+", "-", row["expediente"]).split("-")
                complemento = (row["expediente"]).split(elementos[0] + "/" + elementos[1])
                try:
                    numero = int(elementos[0])
                    ano = int(elementos[1])
                    texto = str(complemento[1])
                except (IndexError, ValueError) as error:
                    click.echo(error)
                    raise error
                if numero < 0:
                    raise ValueError
                if ano < 1900 or ano > date.today().year:
                    raise ValueError
                expediente = f"{str(numero)}/{str(ano)}{str(texto)}"
            except (IndexError, ValueError):
                click.echo("! Expediente no válido " + row["expediente"].strip())
                continue
            # Insertar
            datos = {
                "autoridad": autoridad,
                "expediente": expediente,
                "ubicacion": ubicacion,
            }
            UbicacionExpediente(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} ubicaciones de expedientes alimentadas.")


@click.command()
@click.option("--autoridad-id", default=None, type=int, help="ID de la autoridad")
@click.option("--autoridad-clave", default="", type=str, help="Clave de la autoridad")
@click.option("--output", default="ubicaciones_expedientes.csv", type=str, help="Archivo CSV a escribir")
def respaldar(autoridad_id, autoridad_clave, output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    if autoridad_id:
        autoridad = Autoridad.query.get(autoridad_id)
    elif autoridad_clave:
        autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
    else:
        autoridad = None
    if autoridad is not None and autoridad.es_jurisdiccional is False:
        click.echo("AVISO: La autoridad no es jurisdiccional")
        return
    click.echo("Respaldando ubicaciones de expedientes...")
    contador = 0
    ubicaciones_expedientes = UbicacionExpediente.query.filter_by(estatus="A")
    if autoridad is not None:
        ubicaciones_expedientes = ubicaciones_expedientes.filter(UbicacionExpediente.autoridad == autoridad)
    ubicaciones_expedientes = ubicaciones_expedientes.all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "ubicacion_expediente_id",
                "autoridad_clave",
                "expediente",
                "ubicacion",
            ]
        )
        for ubicacion_expediente in ubicaciones_expedientes:
            respaldo.writerow(
                [
                    ubicacion_expediente.id,
                    ubicacion_expediente.autoridad.clave,
                    ubicacion_expediente.expediente,
                    ubicacion_expediente.ubicacion,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} en {ruta.name}")


@click.command()
@click.argument("autoridad_clave", type=str)
def reiniciar(autoridad_clave):
    """Elimina todas las ubicaciones de expedientes de una autoridad"""

    # Validar autoridad
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave == "":
        click.echo("No es correcta la clave de la autoridad")
        return
    autoridad = Autoridad.query.filter(Autoridad.clave == autoridad_clave).first()
    if autoridad is None:
        click.echo(f"No existe la clave {autoridad_clave} en autoridades")
        return
    if autoridad.estatus != "A":
        click.echo(f"La autoridad {autoridad_clave} no está activa")
        return
    if not autoridad.es_jurisdiccional:
        click.echo(f"La autoridad {autoridad_clave} no es jurisdiccional")
        return
    if autoridad.es_extinto:
        click.echo(f"La autoridad {autoridad_clave} es extinta")
        return
    if autoridad.es_notaria:
        click.echo(f"La autoridad {autoridad_clave} es una notaría")
        return

    # Definir la base de datos
    database = db.session

    # Consultar la cantidad de ubicaciones de expedientes de la autoridad
    ubicaciones_expedientes = database.query(UbicacionExpediente).filter_by(autoridad=autoridad)

    # Si no hay ubicaciones de expedientes, terminar
    if ubicaciones_expedientes.count() == 0:
        click.echo(f"No hay ubicaciones de expedientes para la autoridad {autoridad_clave}")
        return

    # Eliminar todas las ubicaciones de expedientes de la autoridad
    click.echo(f"Eliminando todas las ubicaciones de expedientes de {autoridad_clave}...")
    ubicaciones_expedientes.delete()
    database.commit()


cli.add_command(actualizar)
cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(reiniciar)
