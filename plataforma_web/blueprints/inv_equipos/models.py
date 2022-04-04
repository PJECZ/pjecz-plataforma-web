"""
Inventarios Equipos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvEquipo(db.Model, UniversalMixin):
    """InvEquipo"""

    # Nombre de la tabla
    __tablename__ = "inv_equipos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    inv_custodia_id = db.Column(db.Integer, db.ForeignKey("inv_custodias.id"), index=True, nullable=False)
    inv_custodia = db.relationship("InvCustodia", back_populates="inv_equipos")
    inv_modelo_id = db.Column(db.Integer, db.ForeignKey("inv_modelos.id"), index=True, nullable=False)
    inv_modelo = db.relationship("InvModelo", back_populates="inv_equipos")
    inv_red_id = db.Column(db.Integer, db.ForeignKey("inv_redes.id"), index=True, nullable=False)
    inv_red = db.relationship("InvRed", back_populates="inv_equipos")

    # Columnas
    adquisicion_fecha = db.Column(db.Date())
    numero_serie = db.Column(db.String(256))
    numero_inventario = db.Column(db.Integer())
    descripcion = db.Column(db.String(256), nullable=False)
    direccion_ip = db.Column(db.String(256))
    direccion_mac = db.Column(db.String(256))
    numero_nodo = db.Column(db.Integer())
    numero_switch = db.Column(db.Integer())
    numero_puerto = db.Column(db.Integer())

    # Hijos
    inv_componentes = db.relationship("InvComponente", back_populates="inv_equipo", lazy="noload")
    inv_equipos_fotos = db.relationship("InvEquipoFoto", back_populates="inv_equipo", lazy="noload")

    def __repr__(self):
        """Representación"""
        return "<InvEquipo>"
