"""
Inventarios Equipos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVEquipos(db.Model, UniversalMixin):
    """INVEquipos"""

    # Nombre de la tabla
    __tablename__ = "inv_equipos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    # custodia_id = db.Column(db.Integer, db.ForeignKey('inv_custodia.id'), index=True, nullable=False)
    # custodia_id = db.relationship('InvCustodia', back_populates='equipos')
    modelo_id = db.Column(db.Integer, db.ForeignKey("inv_modelos.id"), index=True, nullable=False)
    modelo = db.relationship("INVModelos", back_populates="equipos")
    # red_id = db.Column(db.Integer, db.ForeignKey('inv_red.id'), index=True, nullable=False)
    # red = db.relationship('InvRed', back_populates='equipos ')

    # Columnas
    adquisicion_fecha = db.Column(db.Date(), nullable=False)
    numero_serie = db.Column(db.String(256))
    numero_inventario = db.Column(db.Integer())
    descripcion = db.Column(db.String(256))
    direccion_ip = db.Column(db.String(256))
    direccion_mac = db.Column(db.String(256))
    numero_nodo = db.Column(db.Integer())
    numero_switch = db.Column(db.Integer())
    numero_puerto = db.Column(db.Integer())

    # Hijos
    componentes = db.relationship("INVComponente", back_populates="equipo")

    def __repr__(self):
        """Representación"""
        return "<InvEquipos>"
