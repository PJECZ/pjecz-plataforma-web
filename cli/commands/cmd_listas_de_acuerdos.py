"""
Listas de Acuerdos

- alimentar: Alimentar la BD a partir de los archivos en Storage
- construir: Construir la estructura de directorios y archivos para el constructor
- respaldar: Respaldar la tabla 'listas_de_acuerdos' a su archivo CSV
- publicar: Publicar el archivo JSON en Storage para que el sitio web lo use con DataTables
"""
from datetime import datetime
from pathlib import Path
import csv
import json
import re
import unicodedata

import click
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.glosas.models import Glosa
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.peritos.models import Perito

app = create_app()
db.app = app

DEPOSITO = "pjecz-consultas"
SUBDIRECTORIO = "Listas de Acuerdos"
LISTAS_DE_ACUERDOS_CSV = "seed/listas_de_acuerdos.csv"
LISTAS_DE_ACUERDOS_JSON = "json/listas_de_acuerdos.json"
PELICAN_CONSULTAS = "/home/guivaloz/Documentos/GitHub/PJECZ/constructor-web-pjecz-gob-mx/content/consultas/listas-de-acuerdos"


def cambiar_a_caracteres_seguros(texto):
    """ Cambia caracteres acentuados a caracteres sin acento, cambia espacios por guiones """
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore")
    texto = texto.decode("utf-8")
    texto = re.sub("[ ]+", "-", texto)
    texto = re.sub("[^0-9a-zA-Z_/-]", "", texto)
    return texto.lower()


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def alimentar():
    """ Alimentar la BD a partir de los archivos en Storage """
    click.echo("Alimentando...")
    # Google Cloud Storage
    client = storage.Client()
    bucket = client.get_bucket(DEPOSITO)
    # Bucle por las autoridades
    contador = 0
    autoridades_activas = Autoridad.query.filter(Autoridad.estatus == "A").all()
    for autoridad in autoridades_activas:
        if autoridad.directorio_listas_de_acuerdos.strip() == "":
            continue
        click.echo(f"  En {autoridad.directorio_listas_de_acuerdos}")
        subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
        # Bucle por los blobs
        blobs = list(bucket.list_blobs(prefix=subdirectorio))
        if len(blobs) == 0:
            click.echo("0 " + subdirectorio)
            continue
        for blob in blobs:
            # Validar
            ruta = Path(blob.name)
            fecha_str = ruta.name[:10]
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            except ValueError:
                continue
            extension = ruta.suffix.lower()
            if extension != ".pdf":
                continue
            descripcion = ruta.name[11 : -len(extension)].strip()
            # Alimentar
            lista_de_acuerdo = ListaDeAcuerdo(
                autoridad=autoridad,
                archivo=ruta.name,
                fecha=fecha,
                descripcion=descripcion,
                url=blob.public_url,
            )
            lista_de_acuerdo.save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Alimentados {contador} registros.")


@click.command()
def construir():
    """ Construir los directorios y archivos para listas de acuerdos """
    # Preparar plantillas
    plantillas_ruta = Path("cli/templates")
    if not (plantillas_ruta.exists() or plantillas_ruta.is_dir()):
        click.echo("No existe el directorio con las plantillas jinja2.")
        return
    plantillas_env = Environment(
        loader=FileSystemLoader(str(plantillas_ruta)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    plantilla = plantillas_env.get_template("lista_de_acuerdo.jinja2")
    # Verificar
    pelican_consultas_ruta = Path(PELICAN_CONSULTAS)
    if not pelican_consultas_ruta.exists():
        click.echo("No existe la pelican_consultas_ruta a los contenidos del Pelican.")
        return
    # Bucle
    contador = 0
    autoridades = Autoridad.query.filter(Autoridad.estatus == "A").all()
    for autoridad in autoridades:
        if autoridad.directorio_listas_de_acuerdos == "":
            continue
        # Directorio
        distrito_str = cambiar_a_caracteres_seguros(autoridad.distrito.nombre)
        # if distrito_str[:12] == "distrito-de-":
        #     distrito_str = distrito_str[12:]
        autoridad_str = cambiar_a_caracteres_seguros(autoridad.descripcion)
        ruta = Path(pelican_consultas_ruta, distrito_str, autoridad_str)
        ruta.mkdir(parents=True, exist_ok=True)
        # Archivo md
        archivo_ruta = Path(ruta, f"{autoridad_str}.md")
        ingredientes = {}
        ingredientes["title"] = f"Listas de Acuerdos {autoridad.descripcion}"
        ingredientes["slug"] = cambiar_a_caracteres_seguros(f"consultas listas de acuerdos {autoridad.distrito.nombre} {autoridad.descripcion}")
        ingredientes["summary"] = "Listas de Acuerdos."
        ingredientes["url"] = ""
        ingredientes["save_as"] = ""
        ingredientes["content"] = "Lista de Acuerdos."
        cocinado = plantilla.render(**ingredientes)
        with open(archivo_ruta, "w") as puntero:
            puntero.write(cocinado)
        click.echo("- " + str(ruta))
        contador += 1
    click.echo(f"Construidos {contador} páginas en listas de acuerdos.")


@click.command()
@click.option("--desde", default="", type=str, help="Fecha de inicio, use AAAA-MM-DD")
def respaldar(desde):
    """ Respaldar la tabla listas_de_acuerdos a su archivo CSV """
    try:
        if desde != "":
            desde_fecha = datetime.strptime(desde, "%Y-%m-%d")
        else:
            desde_fecha = None
    except ValueError:
        click.echo("Fecha desde es incorrecta.")
        return
    click.echo("Respaldando...")
    contador = 0
    if desde_fecha is None:
        listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha).all()
    else:
        listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").filter(ListaDeAcuerdo.fecha >= desde_fecha).order_by(ListaDeAcuerdo.fecha).all()
    with open(LISTAS_DE_ACUERDOS_CSV, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(["autoridad_id", "archivo", "fecha", "descripcion", "url"])
        for lista_de_acuerdo in listas_de_acuerdos:
            escritor.writerow(
                [
                    lista_de_acuerdo.autoridad_id,
                    lista_de_acuerdo.archivo,
                    lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                    lista_de_acuerdo.descripcion,
                    lista_de_acuerdo.url,
                ]
            )
            contador += 1
            if contador % 1000 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} registros en {LISTAS_DE_ACUERDOS_CSV}")


@click.command()
def publicar():
    """Publicar el archivo JSON en Storage para que el sitio web lo use con DataTables
    TODO debe separar y guardar por distrito/autoridad/lista.json
    """
    ruta = Path(LISTAS_DE_ACUERDOS_JSON)
    if not ruta.parent.exists():
        ruta.parent.mkdir(parents=True)
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha).all()
    click.echo("Publicando...")
    registros = []
    for lista_de_acuerdo in listas_de_acuerdos:
        registros.append(
            {
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "archivo": lista_de_acuerdo.archivo,
                "descripcion": lista_de_acuerdo.descripcion,
                "url": lista_de_acuerdo.url,
            }
        )
    datos = {"data": registros}
    with open(ruta, "w") as puntero:
        puntero.write(json.dumps(datos))


cli.add_command(alimentar)
cli.add_command(construir)
cli.add_command(respaldar)
cli.add_command(publicar)
