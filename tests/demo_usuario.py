"""
Usuario
"""
import os
from dotenv import load_dotenv
from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.usuarios.models import Usuario


def main():
    """Main function"""

    # Inicializar
    load_dotenv()  # Take environment variables from .env
    app = create_app()
    db.app = app

    # Obtener el email del usuario
    user_email = os.getenv("RRHH_PERSONAL_API_USERNAME")
    if user_email is None:
        raise ValueError("No se ha especificado la variable de entorno RRHH_PERSONAL_API_USERNAME")

    # Consultar el usuario
    usuario = Usuario.query.filter_by(email=user_email).first()
    print("Nombre completo:", usuario.nombre)

    # Probar la consulta de roles y permisos
    print("Roles:")
    for usuario_rol in usuario.usuarios_roles:
        if usuario_rol.estatus != "A":
            continue
        print("  ", usuario_rol.descripcion)
        for permiso in usuario_rol.rol.permisos:
            if permiso.estatus != "A" or permiso.modulo.estatus != "A":
                continue
            print("    ", permiso.modulo.nombre, permiso.nivel)

    # Probar la consulta de modulos para menu principal
    print("Modulos para menu principal:", str(usuario.modulos_menu_principal))

    # Probar la consulta de permisos
    print("Permisos:", str(usuario.permisos))


if __name__ == "__main__":
    main()
