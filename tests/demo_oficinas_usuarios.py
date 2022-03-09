"""
Demo Oficinas-Usuarios

Consultar a los usuarios que tienen correo electrónico coahuila.gob.mx y que pertenecen a una oficina "generica".

Lo ideal es que este listado salga vacio para que todos los usuarios tengan oficinas definidas.
"""
from dotenv import load_dotenv
from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.usuarios.models import Usuario

def main():
    """Main function"""

    # Inicializar
    load_dotenv()
    app = create_app()
    db.app = app

    # Consultar
    for oficina_clave in ("DACU", "DMON", "DPAR", "DSAB", "DSAL", "DSPC", "DTOR", "ND"):
        oficina = Oficina.query.filter(Oficina.clave==oficina_clave).first()
        if oficina:
            print(oficina.clave, "-", oficina.descripcion)
            usuarios = Usuario.query.\
                filter(Usuario.oficina==oficina).\
                filter(Usuario.email.contains("@coahuila.gob.mx")).\
                filter(Usuario.estatus == "A").all()
            if usuarios:
                for usuario in usuarios:
                    print("  ", usuario.email)

if __name__ == "__main__":
    main()
