"""
Demostracion para obtener los equipos de una oficina
"""
from dotenv import load_dotenv
from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.usuarios.models import Usuario


def main():
    """Proceso principal"""

    # Inicializar
    load_dotenv()
    app = create_app()
    db.app = app

    # Consultar una oficina
    oficina_clave = "DSAL04-DINFO"
    oficina = Oficina.query.filter(Oficina.clave == oficina_clave).first()
    if oficina is None:
        print(f"No se encuentra la oficina {oficina_clave}")
        return

    # Consultar
    inv_equipos = InvEquipo.query.join(InvCustodia, Usuario).filter(InvEquipo.estatus == "A").\
        filter(InvEquipo.inv_custodia_id == InvCustodia.id).\
        filter(InvCustodia.usuario_id == Usuario.id).\
        filter(Usuario.oficina_id == oficina.id).\
        limit(10).all()
    if len(inv_equipos) == 0:
        print(f"No se encontraron equipos para la oficina {oficina_clave}")
        return
    for inv_equipo in inv_equipos:
        print(inv_equipo.id, inv_equipo.descripcion)

if __name__ == "__main__":
    main()
