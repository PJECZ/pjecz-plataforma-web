"""
REPSVM Delitos Genericos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMDelitoGenerico(db.Model, UniversalMixin):
    """REPSVMDelitoGenerico"""

    # Nombre de la tabla
    __tablename__ = "repsvm_delitos_genericos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    repsvm_delitos_especificos = db.relationship("REPSVMDelitoEspecifico", back_populates="repsvm_delito_generico")

    def __repr__(self):
        """Representación"""
        return f"<REPSVMDelitoGenerico {self.nombre}>"
