"""
Usuarios Nominas

- actualizar: Sincronizar con la API de Perseo
"""

from datetime import datetime
from dotenv import load_dotenv
import click
import os
import requests
import sys

from lib.safe_string import safe_curp

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_nominas.models import UsuarioNomina

load_dotenv()  # Take environment variables from .env

PERSEO_API_URL = os.getenv("PERSEO_API_URL")
PERSEO_API_KEY = os.getenv("PERSEO_API_KEY")
TIMEOUT = 12

app = create_app()
db.app = app


@click.group()
def cli():
    """Nóminas"""


@click.command()
def actualizar():
    """Sincronizar con la API de Perseo"""
    click.echo("Sincronizando Nóminas...")

    # Validar que se haya definido PERSEO_URL.
    if PERSEO_API_URL is None:
        click.echo("ERROR: No se ha definido PERSEO_URL.")
        sys.exit(1)

    # Validar que se haya definido PERSEO_API_KEY.
    if PERSEO_API_KEY is None:
        click.echo("ERROR: No se ha definido PERSEO_API_KEY.")
        sys.exit(1)

    # Bucle por los CURP's de Usuarios
    contador = 0
    contador_nuevos = 0
    contador_cambios = 0
    contador_eliminaciones = 0
    for usuario in Usuario.query.filter(Usuario.curp != "").filter_by(estatus="A").order_by(Usuario.curp).all():
        # Consultar a la API
        try:
            respuesta = requests.get(
                f"{PERSEO_API_URL}/v4/timbrados",
                headers={"X-Api-Key": PERSEO_API_KEY},
                params={"curp": usuario.curp},
                timeout=TIMEOUT,
            )
            respuesta.raise_for_status()
        except requests.exceptions.ConnectionError:
            click.echo("ERROR: No hubo respuesta al solicitar usuario")
            sys.exit(1)
        except requests.exceptions.HTTPError as error:
            click.echo("ERROR: Status Code al solicitar usuario: " + str(error))
            sys.exit(1)
        except requests.exceptions.RequestException:
            click.echo("ERROR: Inesperado al solicitar usuario")
            sys.exit(1)
        datos = respuesta.json()
        if "success" not in datos:
            click.echo("ERROR: Fallo al solicitar usuario")
            sys.exit(1)
        if datos["success"] is False:
            if "message" in datos:
                click.echo(f"\n  AVISO: Fallo en usuario {usuario.curp}: {datos['message']}")
            else:
                click.echo(f"\n  AVISO: Fallo en usuario {usuario.curp}")
            continue

        # Si no contiene resultados, saltar
        if len(datos["items"]) == 0:
            click.echo(f"\n  AVISO: La persona con la CURP: {usuario.curp} no tiene timbrados.")
            continue
        items = datos["items"]

        # Bucle para eliminar faltantes
        for timbre in UsuarioNomina.query.filter_by(usuario=usuario).filter_by(estatus="A").all():
            encontrado = False
            for item in items:
                if item["id"] == timbre.timbrado_id:
                    encontrado = True
                    break
            if encontrado is False:
                timbre.delete()
                contador_eliminaciones = contador_eliminaciones + 1
                click.echo("-", nl=False)

        # Bucle para añadir nuevos o actualizar timbres
        for item in items:
            # Verificar si timbrado_id es nuevo
            usuario_nomina = UsuarioNomina.query.filter_by(timbrado_id=item["id"]).filter_by(usuario=usuario).filter_by(estatus="A").first()

            # Añadimos un nuevo timbre a nóminas
            if item["id"] != "" and usuario_nomina is None:
                UsuarioNomina(
                    usuario=usuario,
                    timbrado_id=item["id"],
                    fecha=datetime.strptime(item["nomina_fecha_pago"], "%Y-%m-%d").date(),
                    descripcion=item["nomina_tipo"],
                    archivo_pdf=item["archivo_pdf"],
                    archivo_xml=item["archivo_xml"],
                    url_pdf=item["url_pdf"],
                    url_xml=item["url_xml"],
                ).save()
                contador_nuevos = contador_nuevos + 1
                click.echo(".", nl=False)
                continue

            # Buscar actualizaciones
            hay_cambios = False

            fecha = datetime.strptime(item["nomina_fecha_pago"], "%Y-%m-%d").date()
            if fecha != usuario_nomina.fecha:
                hay_cambios = True
            if usuario_nomina.archivo_pdf != item["archivo_pdf"]:
                hay_cambios = True
            if usuario_nomina.url_pdf != item["url_pdf"]:
                hay_cambios = True
            if usuario_nomina.archivo_xml != item["archivo_xml"]:
                hay_cambios = True
            if usuario_nomina.url_xml != item["url_xml"]:
                hay_cambios = True

            # Hacer actualización del registro
            if hay_cambios:
                usuario_nomina.fecha = fecha
                usuario_nomina.archivo_pdf = item["archivo_pdf"]
                usuario_nomina.url_pdf = item["url_pdf"]
                usuario_nomina.archivo_xml = item["archivo_xml"]
                usuario_nomina.url_xml = item["url_xml"]
                usuario_nomina.save()
                contador_cambios = contador_cambios + 1
                click.echo("+", nl=False)

        contador += 1
        if contador % 100 == 0:
            click.echo(f"\n  Van {contador}...")

    # Mensaje de termino
    click.echo("")
    click.echo(f"Hubo {contador_nuevos} timbres nuevos copiados.")
    click.echo(f"Hubo {contador_cambios} timbres actualizados.")
    click.echo(f"Hubo {contador_eliminaciones} timbres eliminados.")


@click.command()
@click.argument("curp", type=str)
def actualizar_usuario(curp):
    """Sincronizar un usuario con la API de Perseo"""
    click.echo("Sincronizando Nóminas para un usuario...")

    # Validar que se haya definido PERSEO_URL.
    if PERSEO_API_URL is None:
        click.echo("ERROR: No se ha definido PERSEO_URL.")
        sys.exit(1)

    # Validar que se haya definido PERSEO_API_KEY.
    if PERSEO_API_KEY is None:
        click.echo("ERROR: No se ha definido PERSEO_API_KEY.")
        sys.exit(1)

    for usuario in Usuario.query.filter(Usuario.curp == curp).filter_by(estatus="A").all():
        # Consultar a la API
        try:
            respuesta = requests.get(
                f"{PERSEO_API_URL}/v4/timbrados",
                headers={"X-Api-Key": PERSEO_API_KEY},
                params={"curp": safe_curp(curp)},
                timeout=TIMEOUT,
            )
            respuesta.raise_for_status()
        except requests.exceptions.ConnectionError:
            click.echo("ERROR: No hubo respuesta al solicitar usuario")
            sys.exit(1)
        except requests.exceptions.HTTPError as error:
            click.echo("ERROR: Status Code al solicitar usuario: " + str(error))
            sys.exit(1)
        except requests.exceptions.RequestException:
            click.echo("ERROR: Inesperado al solicitar usuario")
            sys.exit(1)
        datos = respuesta.json()
        if "success" not in datos:
            click.echo("ERROR: Fallo al solicitar usuario")
            sys.exit(1)
        if datos["success"] is False:
            if "message" in datos:
                click.echo(f"  AVISO: Fallo en usuario {usuario.curp}: {datos['message']}")
            else:
                click.echo(f"  AVISO: Fallo en usuario {usuario.curp}")
            continue

        # Si no contiene resultados, saltar
        if len(datos["items"]) == 0:
            click.echo(f"  AVISO: La persona con la CURP: {curp} no tiene timbrados.")
            continue
        items = datos["items"]

        click.echo(f"Procesando al usuario {usuario.nombre} - {usuario.email}")

        # Bucle para eliminar faltantes
        for timbre in UsuarioNomina.query.filter_by(usuario=usuario).filter_by(estatus="A").all():
            encontrado = False
            for item in items:
                if item["id"] == timbre.timbrado_id:
                    encontrado = True
                    break
            if encontrado is False:
                timbre.delete()
                click.echo("  - Eliminando timbre anterior")

        # Bucle para añadir nuevos o actualizar timbres
        for item in items:
            # Verificar si timbrado_id es nuevo
            usuario_nomina = UsuarioNomina.query.filter_by(timbrado_id=item["id"]).filter_by(usuario=usuario).filter_by(estatus="A").first()

            # Añadimos un nuevo timbre a nóminas
            if item["id"] != "" and usuario_nomina is None:
                UsuarioNomina(
                    usuario=usuario,
                    timbrado_id=item["id"],
                    fecha=datetime.strptime(item["nomina_fecha_pago"], "%Y-%m-%d").date(),
                    descripcion=item["nomina_tipo"],
                    archivo_pdf=item["archivo_pdf"],
                    archivo_xml=item["archivo_xml"],
                    url_pdf=item["url_pdf"],
                    url_xml=item["url_xml"],
                ).save()
                click.echo("  + Nuevo timbre agregado")
                continue

            # Buscar actualizaciones
            hay_cambios = False

            fecha = datetime.strptime(item["nomina_fecha_pago"], "%Y-%m-%d").date()
            if fecha != usuario_nomina.fecha:
                hay_cambios = True
            if usuario_nomina.archivo_pdf != item["archivo_pdf"]:
                hay_cambios = True
            if usuario_nomina.url_pdf != item["url_pdf"]:
                hay_cambios = True
            if usuario_nomina.archivo_xml != item["archivo_xml"]:
                hay_cambios = True
            if usuario_nomina.url_xml != item["url_xml"]:
                hay_cambios = True

            # Hacer actualización del registro
            if hay_cambios:
                usuario_nomina.fecha = fecha
                usuario_nomina.archivo_pdf = item["archivo_pdf"]
                usuario_nomina.url_pdf = item["url_pdf"]
                usuario_nomina.archivo_xml = item["archivo_xml"]
                usuario_nomina.url_xml = item["url_xml"]
                usuario_nomina.save()
                click.echo("  ~ Hubo cambios en el timbre")


cli.add_command(actualizar)
cli.add_command(actualizar_usuario)
