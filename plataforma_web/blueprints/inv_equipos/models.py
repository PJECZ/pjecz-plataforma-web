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
    # inv_custodia_id = db.Column(db.Integer, db.ForeignKey('inv_custodia.id'), index=True, nullable=False)
    # inv_custodia_id = db.relationship('InvCustodia', back_populates='inv_equipos ')
    # inv_modelo_id = db.Column(db.Integer, db.ForeignKey('inv_modelo.id'), index=True, nullable=False)
    # inv_modelo_id = db.relationship('InvModelo', back_populates='inv_equipos ')
    # inv_red_id = db.Column(db.Integer, db.ForeignKey('inv_red.id'), index=True, nullable=False)
    # inv_red_id = db.relationship('InvRed', back_populates='inv_equipos ')

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
    # plural_hijos = db.relationship("Clase_hijo", back_populates="singular_esta_clase")

    def __repr__(self):
        """Representación"""
        return "<InvEquipos>"
