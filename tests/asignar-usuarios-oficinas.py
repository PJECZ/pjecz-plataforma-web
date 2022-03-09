"""
Usuarios-Oficinas

Asignacion masiva de usuarios a sus oficinas, si no tienen asignadas ninguna
"""
import csv
import argparse
from pathlib import Path
from dotenv import load_dotenv
from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.oficinas.models import Oficina

USUARIOS_OFICINAS_CSV = "seed/usuarios_oficinas.csv"

# Definir las equivalencias entre distrito_nombre y la oficina
OFICINAS_POR_DEFECTO = [
    "ND",
    "DACU",
    "DMON",
    "DPAR",
    "DRGR",
    "DSAB",
    "DSAL",
    "DSPC",
    "DTOR",
]


def main():
    """Main function"""

    # Inicializar
    load_dotenv()  # Take environment variables from .env
    app = create_app()
    db.app = app

    # Simulacion o ejecucion
    simulacion = True
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--exec", help="Ejecutar cambio en la BD", action="store_true")
    args = parser.parse_args()
    if args.exec:
        simulacion = False
    msg_exec = "SIMULACION" if simulacion else "EJECUCIÓN"
    print(f"Alimentando relación de oficinas con usuarios... {msg_exec}")

    # Ruta al archivo CSV
    ruta = Path(USUARIOS_OFICINAS_CSV)
    if not ruta.exists():
        print(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        print(f"AVISO: {ruta.name} no es un archivo.")
        return

    # Bucle para leer cada linea del archivo CSV
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Validar usuario
            if "usuario_email" in row:
                usuario_email = row["usuario_email"]
                usuario = Usuario.query.join(Oficina).filter(Usuario.email==usuario_email).first()
                if usuario is None:
                    print(f"  No se encontró el usuario con el email {usuario_email}")
                    continue
                if usuario.oficina.clave not in OFICINAS_POR_DEFECTO:
                    print(f"  Este usuario ya tiene una oficina asignada. {usuario_email}={usuario.oficina.clave}")
                    continue
            else:
                raise Exception("  ERROR: No tiene la columna usuario_email")
            # Validar Oficina
            if "oficina_clave" in row:
                oficina_clave = row["oficina_clave"]
                oficina = Oficina.query.filter_by(clave=oficina_clave).first()
                if oficina is None:
                    print(f"  No se encentra la oficina con la clave {oficina_clave}")
                    continue
            else:
                raise Exception("  ERROR: No tiene la columna oficina_clave")
            # Hacer la asignación
            if simulacion:
                print(f"UPDATE {usuario_email} = {oficina_clave}")
            else:
                usuario.oficina=oficina
                usuario.save()
            # Incrementar contador
            contador += 1
            if contador % 100 == 0:
                print(f"  Van {contador} relaciones...")
    # Mensaje final
    print(f"={contador} usuarios asignados a una nueva oficina. {msg_exec}")


if __name__ == "__main__":
    main()
