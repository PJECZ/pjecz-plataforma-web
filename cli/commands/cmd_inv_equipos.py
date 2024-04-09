"""
Inventarios Equipos

- alimentar: Insertar equipos a partir de un archivo CSV
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

import click

from lib.safe_string import safe_email, safe_string
from plataforma_web.app import create_app
from plataforma_web.blueprints.inv_categorias.models import InvCategoria
from plataforma_web.blueprints.inv_componentes.models import InvComponente
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_marcas.models import InvMarca
from plataforma_web.blueprints.inv_modelos.models import InvModelo
from plataforma_web.blueprints.inv_redes.models import InvRed
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.extensions import db

app = create_app()
db.app = app

INV_RED_ID = 3  # No Aplica


@click.group()
@click.pass_context
def cli(ctx):
    """Inventarios Equipos"""


@cli.command()
@click.argument("archivo_csv", type=str)
@click.option("--descripcion", default=None, help="Descripcion")
@click.option("--fecha_fabricacion", default=None, help="Fecha de fabricacion")
@click.option("--inv_custodia_id", default=None, help="ID de la custodia")
@click.option("--inv_modelo_id", default=None, help="ID del modelo")
@click.option("--tipo", default=None, help="Tipo")
@click.pass_context
def agregar_actualizar(ctx, archivo_csv, descripcion, fecha_fabricacion, inv_custodia_id, inv_modelo_id, tipo):
    """Agregar o actualizar inv_equipos a partir de un archivo CSV"""

    # Validar archivo CSV
    ruta = Path(archivo_csv)
    if not ruta.exists():
        click.echo(f"ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)

    # Validar descripcion
    if descripcion is not None:
        descripcion = safe_string(descripcion)

    # Validar fecha de fabricacion
    if fecha_fabricacion is not None:
        try:
            fecha_fabricacion = datetime.strptime(fecha_fabricacion, "%Y-%m-%d").date()
        except ValueError:
            click.echo("ERROR: La fecha de fabricacion debe de tener el formato YYYY-MM-DD")
            sys.exit(1)

    # Validar custodia
    if inv_custodia_id is not None:
        if InvCustodia.query.get(inv_custodia_id) is None:
            click.echo(f"ERROR: No existe la custodia con ID {inv_custodia_id}")
            sys.exit(1)

    # Validar modelo
    if inv_modelo_id is not None:
        if InvModelo.query.get(inv_modelo_id) is None:
            click.echo(f"ERROR: No existe el modelo con ID {inv_modelo_id}")
            sys.exit(1)

    # Validar tipo
    if tipo is not None:
        if tipo not in InvEquipo.TIPOS:
            click.echo(f"ERROR: No existe el tipo {tipo}")
            sys.exit(1)

    # Inicializar listados
    inv_equipos_actualizados = []

    # Inicializar contadores
    contador_inv_equipos_agregados = 0
    contador_inv_equipos_actualizados = 0
    contador_inv_equipos_sin_numero_serie = 0

    # Leer el archivo CSV
    click.echo("Agregando o actualizando inv_equipos a partir de un archivo CSV: ", nl=False)
    with open(ruta, newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_inv_custodia_id = None
            data_usuario_email = None
            data_inv_modelo_id = None
            data_marca_nombre = None
            data_modelo_descripcion = None
            data_inv_red_id = None
            data_red_nombre = None
            data_fecha_fabricacion = None
            data_numero_serie = None
            data_numero_inventario = 0
            data_tipo = None
            data_descripcion = descripcion
            # Tomar los datos del renglon
            try:
                if inv_custodia_id is None:
                    if row["Custodia"] != "":
                        data_inv_custodia_id = int(row["Custodia"])
                    if row["Usuario e-mail"] != "":
                        data_usuario_email = safe_email(row["Usuario e-mail"])
                if inv_modelo_id is None:
                    if row["Marca"] != "":
                        data_marca_nombre = safe_string(row["Marca"])
                    if row["Modelo"] != "":
                        data_modelo_descripcion = safe_string(row["Modelo"])
                if safe_string(row["Red"]) != "":
                    data_red_nombre = safe_string(row["Red"])
                if fecha_fabricacion is None and row["F. Fab."] != "":
                    data_fecha_fabricacion = row["F. Fab."]
                if safe_string(row["No. Serie"]) != "":
                    data_numero_serie = safe_string(row["No. Serie"])
                if row["No. Inv."] != "":
                    data_numero_inventario = int(row["No. Inv."])
                if tipo is None and safe_string(row["Tipo"]) != "":
                    data_tipo = safe_string(row["Tipo"])
                data_direccion_ip = safe_string(row["D. IP"])
                data_direccion_mac = safe_string(row["Mac Address"])
                data_disco_duro_descripcion = safe_string(row["Disco Duro"])
                data_memoria_ram_descripcion = safe_string(row["Memoria"])
                data_procesador_descripcion = safe_string(row["Procesador"])
            except (KeyError, ValueError) as error:
                click.echo(f"ERROR: No se encontró la columna {error}")
                sys.exit(1)

            # Si no hay numero de serie, incrementar contador y continuar con el siguiente renglon
            if data_numero_serie is None:
                contador_inv_equipos_sin_numero_serie += 1
                click.echo("x", nl=False)
                continue

            # Si hay parametro para inv_custodia_id, debe imponese
            if inv_custodia_id is not None:
                data_inv_custodia_id = inv_custodia_id
            # Si NO tenemos data_inv_custodia_id, buscar la custodia con usuario_email
            elif data_inv_custodia_id is None and data_usuario_email is not None:
                # Buscar al usuario con el usuario_email
                usuario = Usuario.query.filter_by(email=data_usuario_email).filter_by(estatus="A").first()
                # Si no se encontro, mostrar error y salir
                if usuario is None:
                    click.echo(f"ERROR: No se encontro el usuario {data_usuario_email}")
                    sys.exit(1)
                # Buscar la custodia del usuario
                inv_custodia = InvCustodia.query.filter_by(usuario_id=usuario.id).filter_by(estatus="A").order_by(InvCustodia.id.desc()).first()
                # Si no se encontro la custodia, mostrar error y salir
                if inv_custodia is None:
                    click.echo(f"ERROR: No se encontro la custodia del usuario {data_usuario_email}")
                    sys.exit(1)
                data_inv_custodia_id = inv_custodia.id
            # No se tiene inv_custodia_id ni usuario_email, mostrar error y salir
            else:
                click.echo("ERROR: No se tiene inv_custodia_id ni usuario_email")
                sys.exit(1)

            # Si hay parametro para inv_modelo_id, debe imponerse
            if inv_modelo_id is not None:
                data_inv_modelo_id = inv_modelo_id
            # De lo contrario, buscar el modelo con marca_nombre y modelo_descripcion
            elif inv_modelo_id is None:
                marca = InvMarca.query.filter_by(nombre=data_marca_nombre).first()
                if marca is None:
                    click.echo(f"ERROR: No existe la marca {data_marca_nombre}")
                    sys.exit(1)
                modelo = InvModelo.query.filter_by(inv_marca_id=marca.id, descripcion=data_modelo_descripcion).first()
                if modelo is None:
                    click.echo(f"ERROR: No existe el modelo {data_modelo_descripcion} de la marca {data_marca_nombre}")
                    sys.exit(1)
                data_inv_modelo_id = modelo.id
                data_descripcion = f"{marca.nombre} - {modelo.descripcion}"

            # Si hay data_red_nombre, consultar el id de la red
            if data_red_nombre is not None:
                red = InvRed.query.filter_by(nombre=data_red_nombre).first()
                if red is None:
                    click.echo(f"ERROR: No existe la red {data_red_nombre}")
                    sys.exit(1)
                data_inv_red_id = red.id
            else:
                data_inv_red_id = INV_RED_ID

            # Si hay parametro para fecha_fabricacion, debe imponerse
            if fecha_fabricacion is not None:
                data_fecha_fabricacion = fecha_fabricacion
            # De lo contrario, si data_fecha_fabricacion es string, convertirla a datetime
            elif isinstance(data_fecha_fabricacion, str):
                try:
                    data_fecha_fabricacion = datetime.strptime(data_fecha_fabricacion, "%Y-%m-%d").date()
                except ValueError:
                    click.echo("ERROR: La fecha de fabricacion debe de tener el formato YYYY-MM-DD")
                    sys.exit(1)
            # De lo contrario, NO hay fecha de fabricacion
            else:
                data_fecha_fabricacion = None

            # Si hay parametro para tipo, debe imponerse
            if tipo is not None:
                data_tipo = tipo
            # De lo contrarrio, validar data_tipo
            elif data_tipo not in InvEquipo.TIPOS:
                click.echo(f"ERROR: No existe el tipo {data_tipo}")
                sys.exit(1)

            # Revisar si el equipo ya existe buscando por el numero de serie
            inv_equipo = InvEquipo.query.filter_by(numero_serie=data_numero_serie).filter_by(estatus="A").order_by(InvEquipo.id.desc()).first()

            # Si el equipo no existe, se agrega
            if inv_equipo is None:
                inv_equipo = InvEquipo(
                    inv_custodia_id=data_inv_custodia_id,
                    inv_modelo_id=data_inv_modelo_id,
                    inv_red_id=data_inv_red_id,
                    fecha_fabricacion=data_fecha_fabricacion,
                    tipo=data_tipo,
                    descripcion=data_descripcion,
                    numero_serie=data_numero_serie,
                    numero_inventario=data_numero_inventario,
                    direccion_ip=data_direccion_ip,
                    direccion_mac=data_direccion_mac,
                )
                inv_equipo.save()

                # Agregar el componente disco duro
                if data_disco_duro_descripcion != "":
                    inv_categoria = InvCategoria.query.filter_by(nombre="DISCO DURO").first()
                    inv_componente = InvComponente(
                        inv_categoria_id=inv_categoria.id,
                        inv_equipo_id=inv_equipo.id,
                        descripcion=data_disco_duro_descripcion,
                        cantidad=1,
                    )
                    inv_componente.save()

                # Agregar el componente memoria ram
                if data_memoria_ram_descripcion != "":
                    inv_categoria = InvCategoria.query.filter_by(nombre="MEMORIA RAM").first()
                    inv_componente = InvComponente(
                        inv_categoria_id=inv_categoria.id,
                        inv_equipo_id=inv_equipo.id,
                        descripcion=data_memoria_ram_descripcion,
                        cantidad=1,
                    )
                    inv_componente.save()

                # Agregar el componente procesador
                if data_procesador_descripcion != "":
                    inv_categoria = InvCategoria.query.filter_by(nombre="PROCESADOR").first()
                    inv_componente = InvComponente(
                        inv_categoria_id=inv_categoria.id,
                        inv_equipo_id=inv_equipo.id,
                        descripcion=data_procesador_descripcion,
                        cantidad=1,
                    )
                    inv_componente.save()

                # Continuar con el siguiente renglon
                contador_inv_equipos_agregados += 1
                click.echo("+", nl=False)
                continue

            # A partir de aqui, el equipo ya existe, inicializar la bandera hay_cambios
            hay_cambios = False

            # Si es diferente inv_custodia_id, actualizar
            if inv_equipo.inv_custodia_id != data_inv_custodia_id:
                inv_equipo.inv_custodia_id = data_inv_custodia_id
                hay_cambios = True

            # Si es diferente inv_modelo_id, actualizar
            if inv_equipo.inv_modelo_id != data_inv_modelo_id:
                inv_equipo.inv_modelo_id = data_inv_modelo_id
                hay_cambios = True

            # Si es diferente inv_red_id, actualizar
            if inv_equipo.inv_red_id != data_inv_red_id:
                inv_equipo.inv_red_id = data_inv_red_id
                hay_cambios = True

            # Si es diferente fecha_fabricacion, actualizar
            if inv_equipo.fecha_fabricacion != data_fecha_fabricacion:
                inv_equipo.fecha_fabricacion = data_fecha_fabricacion
                hay_cambios = True

            # Si es diferente tipo, actualizar
            if inv_equipo.tipo != data_tipo:
                inv_equipo.tipo = data_tipo
                hay_cambios = True

            # Si es diferente descripcion, actualizar
            if inv_equipo.descripcion != data_descripcion:
                inv_equipo.descripcion = data_descripcion
                hay_cambios = True

            # Si es diferente numero_inventario, actualizar
            if inv_equipo.numero_inventario != data_numero_inventario:
                inv_equipo.numero_inventario = data_numero_inventario
                hay_cambios = True

            # Si hay cambios, guardar
            if hay_cambios:
                inv_equipo.save()
                contador_inv_equipos_actualizados += 1
                inv_equipos_actualizados.append(inv_equipo)
                click.echo("u", nl=False)

    # Poner avance de linea
    click.echo("")

    # Si hubo equipos sin numero de serie, mostrar contador
    if contador_inv_equipos_sin_numero_serie > 0:
        click.echo(f"Se omitieron {contador_inv_equipos_sin_numero_serie} equipos por no tener numero de serie")

    # Si hubo equipos agregados, mostrar contador
    if contador_inv_equipos_agregados > 0:
        click.echo(f"Se agregaron {contador_inv_equipos_agregados} equipos")

    # Si hubo equipos actualizados, mostrar contador
    if contador_inv_equipos_actualizados > 0:
        click.echo(f"Se actualizaron {contador_inv_equipos_actualizados} equipos")


cli.add_command(agregar_actualizar)
