"""
CONATRIB

Prueba para mostrar los contenidos del depósito.
"""
import json
from pathlib import Path
import click
import googleapiclient.discovery
from google.cloud import storage

DEPOSITO = "conatrib-pjecz-gob-mx"


def create_service():
    """ Creates the service object for calling the Cloud Storage API """
    return googleapiclient.discovery.build("storage", "v1")


def get_bucket_metadata(bucket):
    """ Retrieves metadata about the given bucket """
    service = create_service()
    req = service.buckets().get(bucket=bucket)
    return req.execute()


def list_bucket(bucket):
    """ Returns a list of metadata of the objects within the given bucket """
    service = create_service()
    fields_to_return = "nextPageToken,items(name,size,contentType,metadata(my-key))"
    req = service.objects().list(bucket=bucket, fields=fields_to_return)
    all_objects = []
    while req:
        resp = req.execute()
        all_objects.extend(resp.get("items", []))
        req = service.objects().list_next(req, resp)
    return all_objects


@click.group()
def cli():
    """ Grupo para una orden click """


@click.command()
def mostrar_api():
    """ Mostrar los archivos en el storage de CONATRIB como JSON """
    click.echo("Mostrando...")
    click.echo(json.dumps(get_bucket_metadata(DEPOSITO), indent=2))
    click.echo(json.dumps(list_bucket(DEPOSITO), indent=2))


@click.command()
def mostrar_blob():
    """ Mostrar los archivos en el storage de CONATRIB como texto """
    click.echo("Mostrando...")
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(DEPOSITO)
    for blob in blobs:
        print(blob.name)


@click.command()
@click.argument("archivo")
@click.option("--nombre", default="", type=str, help="Nombre que va a tener en el depósito")
def subir(archivo, nombre):
    """ Subir un archivo """
    click.echo(f"Subiendo {archivo}...")
    ruta = Path(archivo)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    if nombre == "":
        nombre = ruta.name
    storage_client = storage.Client()
    bucket = storage_client.bucket(DEPOSITO)
    blob = bucket.blob(nombre)
    blob.upload_from_filename(ruta)
    click.echo("Listo.")


cli.add_command(mostrar_api)
cli.add_command(mostrar_blob)
cli.add_command(subir)
