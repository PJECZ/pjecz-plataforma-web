"""
Respaldar Funcionarios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.autoridades_funcionarios.models import AutoridadFuncionario
from plataforma_web.blueprints.funcionarios.models import Funcionario


def respaldar_funcionarios(salida: str = "funcionarios.csv"):
    """Respaldar Funcionarios a un archivo CSV"""
    ruta = Path(salida)
    if ruta.exists():
        click.echo(f"AVISO: {salida} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando funcionarios...")
    contador = 0
    funcionarios = Funcionario.query.order_by(Funcionario.id).all()
    with open(ruta, "w", encoding="utf-8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "funcionario_id",
                "autoridades_claves",
                "nombres",
                "apellido_paterno",
                "apellido_materno",
                "curp",
                "email",
                "puesto",
                "telefono",
                "extension",
                "domicilio_oficial",
                "ingreso_fecha",
                "puesto_clave",
                "fotografia_url",
                "en_funciones",
                "en_sentencias",
                "en_soportes",
                "en_tesis_jurisprudencias",
                "estatus",
            ]
        )
        for funcionario in funcionarios:
            autoridades_claves = []
            for autoridad_funcionario in AutoridadFuncionario.query.filter_by(funcionario_id=funcionario.id).filter_by(estatus='A').all():
                autoridades_claves.append(autoridad_funcionario.autoridad.clave)
            respaldo.writerow(
                [
                    funcionario.id,
                    ",".join(autoridades_claves),
                    funcionario.nombres,
                    funcionario.apellido_paterno,
                    funcionario.apellido_materno,
                    funcionario.curp,
                    funcionario.email,
                    funcionario.puesto,
                    funcionario.telefono,
                    funcionario.extension,
                    funcionario.domicilio_oficial,
                    funcionario.ingreso_fecha,
                    funcionario.puesto_clave,
                    funcionario.fotografia_url,
                    int(funcionario.en_funciones),
                    int(funcionario.en_sentencias),
                    int(funcionario.en_soportes),
                    int(funcionario.en_tesis_jurisprudencias),
                    funcionario.estatus,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} en {ruta.name}")
