"""
Inventarios Equipos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVEquipo(db.Model, UniversalMixin):
    """INVEquipo"""

    # Nombre de la tabla
    __tablename__ = "inv_equipos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    inv_custodia_id = db.Column(db.Integer, db.ForeignKey("inv_custodias.id"), index=True, nullable=False)
    custodia = db.relationship("INVCustodia", back_populates="equipos")
    inv_modelo_id = db.Column(db.Integer, db.ForeignKey("inv_modelos.id"), index=True, nullable=False)
    modelo = db.relationship("INVModelo", back_populates="equipos")
    inv_red_id = db.Column(db.Integer, db.ForeignKey("inv_redes.id"), index=True, nullable=False)
    red = db.relationship("INVRedes", back_populates="equipos")

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
    componentes = db.relationship("INVComponente", back_populates="equipo")
    fotos = db.relationship("INVEquipoFoto", back_populates="equipo")

    def __repr__(self):
        """Representación"""
        return "<InvEquipo>"
