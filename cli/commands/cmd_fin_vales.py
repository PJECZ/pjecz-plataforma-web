"""
Financieros Vales
"""
from datetime import datetime
import json
import os
import click

from dotenv import load_dotenv
import requests

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.fin_vales.models import FinVale

load_dotenv()  # Take environment variables from .env

app = create_app()
db.app = app

EFIRMA_SERVICIO_FIRMA_CADENA_URL = os.getenv("EFIRMA_SERVICIO_FIRMA_CADENA_URL")
EFIRMA_REG_IDENT = os.getenv("EFIRMA_REG_IDENT")
EFIRMA_REG_PASS = os.getenv("EFIRMA_REG_PASS")
EFIRMA_APP_ID = os.getenv("EFIRMA_APP_ID")
EFIRMA_APP_PASS = os.getenv("EFIRMA_APP_PASS")


@click.group()
def cli():
    """Financieros Vales"""
    if EFIRMA_SERVICIO_FIRMA_CADENA_URL is None:
        click.echo("Falta configurar EFIRMA_SERVICIO_FIRMA_CADENA_URL")
        return
    if EFIRMA_REG_IDENT is None:
        click.echo("Falta configurar EFIRMA_REG_IDENT")
        return
    if EFIRMA_REG_PASS is None:
        click.echo("Falta configurar EFIRMA_REG_PASS")
        return
    if EFIRMA_REG_PASS is None:
        click.echo("Falta configurar EFIRMA_APP_ID")
        return
    if EFIRMA_APP_PASS is None:
        click.echo("Falta configurar EFIRMA_APP_PASS")
        return


@click.command()
@click.argument("fin_vale_id")
def solicitar(fin_vale_id):
    """Firmar un vale"""

    # Validar vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        click.echo("No se encontró el vale")
        return
    if fin_vale.estatus != "A":
        click.echo("El vale esta eliminado")
        return
    click.echo(f'Voy a firmar el vale "{fin_vale.justificacion}"')

    # Firmar el vale
    elementos = {
        "id": fin_vale.id,
        "autorizo": fin_vale.autorizo_nombre,
        "creado": fin_vale.creado.strftime("%Y-%m-%d %H:%M:%S"),
        "justificacion": fin_vale.justificacion,
        "monto": fin_vale.monto,
        "solicito": fin_vale.solicito_nombre,
        "tipo": fin_vale.tipo,
    }
    data = {
        "cadenaOriginal": json.dumps(elementos),
        "idRegistro": EFIRMA_REG_IDENT,
        "contrasenaRegistro": EFIRMA_REG_PASS,
        "idAplicacion": EFIRMA_APP_ID,
        "contrasenaAplicacion": EFIRMA_APP_PASS,
        "referencia": fin_vale_id,
        "verificarUrl": True,
    }
    response = requests.post(
        EFIRMA_SERVICIO_FIRMA_CADENA_URL,
        data=data,
        verify=False,
    )
    click.echo(f"Codigo de respuesta: {response.status_code}")
    click.echo(f"Respuesta: {response.text}")

    # Validar que el codigo de respuesta sea 200
    if response.status_code != 200:
        click.echo("Error al firmar el vale porque la respuesta no es 200")
        return

    # Validar
    datos = json.loads(response.text)
    if datos["success"] is False:
        click.echo("Error al firmar el vale porque la respuesta no es success")
        return

    # Actualizar el vale
    fin_vale.solicito_efirma_tiempo = datetime.strptime(datos.fecha, "%d/%m/%Y %H:%M:%S")
    fin_vale.solicito_efirma_folio = datos.folio
    fin_vale.solicito_efirma_selloDigital = datos.selloDigital
    fin_vale.solicito_efirma_url = datos.url
    fin_vale.solicito_efirma_qr_url = ""
    fin_vale.estado = "SOLICITADO"
    fin_vale.save()


# Respuesta:
#   "success": true,
#   "folio": 000001,
#   "mensaje": "La operación se ha realizado exitosamente.",
#   "cadenaOriginal": "",
#   "fecha": "27/06/2022 13:47:11",
#   "selloDigital": "",
#   "url": "https://servidor/eFirmaServicios/verificaFirmaCadena.do?verificar=ZhSsI%2FYUG9soc%2FkTfsWVvoUpylEwvoq%2F",
#   "ip": "172.1.1.1",
#   "huella": "Primer mensaje de prueba"


cli.add_command(solicitar)
