"""
Financieros Vales
"""
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


@click.command()
@click.argument("fin_vale_id")
def firmar(fin_vale_id):
    """Firmar un vale"""
    fin_vale = FinVale.query.get(fin_vale_id)
    click.echo(f"EFIRMA_SERVICIO_FIRMA_CADENA_URL: {EFIRMA_SERVICIO_FIRMA_CADENA_URL}")
    click.echo(f"EFIRMA_REG_IDENT: {EFIRMA_REG_IDENT}")
    click.echo(f"EFIRMA_REG_PASS: {EFIRMA_REG_PASS}")
    click.echo(f"EFIRMA_APP_ID: {EFIRMA_APP_ID}")
    click.echo(f"EFIRMA_APP_PASS: {EFIRMA_APP_PASS}")
    click.echo(f'Voy a firmar el vale "{fin_vale.justificacion}"')
    elementos = [
        fin_vale.autorizo_nombre,
        fin_vale.autorizo_puesto,
        fin_vale.tipo,
        fin_vale.justificacion,
        str(fin_vale.monto),
        fin_vale.solicito_nombre,
        fin_vale.solicito_puesto,
    ]
    response = requests.post(
        EFIRMA_SERVICIO_FIRMA_CADENA_URL,
        data={
            "cadenaOriginal": "|".join(elementos),
            "idRegistro": EFIRMA_REG_IDENT,
            "contrasenaRegistro": EFIRMA_REG_PASS,
            "idAplicacion": EFIRMA_APP_ID,
            "contrasenaAplicacion": EFIRMA_APP_PASS,
            "referencia": fin_vale_id,
            "verificarUrl": True,
        },
        verify=False,
    )
    click.echo(f"Codigo de respuesta: {response.status_code}")
    click.echo(f"Respuesta: {response.text}")


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


cli.add_command(firmar)
