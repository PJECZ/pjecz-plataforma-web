"""
REPSVM Delitos Especificos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMDelitoEspecifico(db.Model, UniversalMixin):
    """REPSVMDelitoEspecifico"""

    # Nombre de la tabla
    __tablename__ = "repsvm_delitos_especificos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    repsvm_delito_generico_id = db.Column(db.Integer, db.ForeignKey("repsvm_delitos_genericos.id"), index=True, nullable=False)
    repsvm_delito_generico = db.relationship("REPSVMDelitoGenerico", back_populates="repsvm_delitos_especificos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    repsvm_agresores = db.relationship("REPSVMAgresor", back_populates="repsvm_delito_especifico")

    def __repr__(self):
        """Representación"""
        return f"<REPSVMDelitoEspecifico {self.descripcion}>"
