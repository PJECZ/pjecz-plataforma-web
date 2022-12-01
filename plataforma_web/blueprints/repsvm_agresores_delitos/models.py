"""
REPSVM Agresores-Delitos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMAgresorDelito(db.Model, UniversalMixin):
    """REPSVMAgresorDelito"""

    # Nombre de la tabla
    __tablename__ = "repsvm_agresores_delitos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    repsvm_agresor_id = db.Column(db.Integer, db.ForeignKey("repsvm_agresores.id"), index=True, nullable=False)
    repsvm_agresor = db.relationship("REPSVMAgresor", back_populates="repsvm_agresores_delitos")
    repsvm_delito_id = db.Column(db.Integer, db.ForeignKey("repsvm_delitos.id"), index=True, nullable=False)
    repsvm_delito = db.relationship("REPSVMDelito", back_populates="repsvm_agresores_delitos")

    # Hijos
    plural_hijos = db.relationship("Clase_hijo", back_populates="singular_esta_clase", lazy="noload")

    def __repr__(self):
        """Representación"""
        return "<REPSVMAgresorDelito>"
