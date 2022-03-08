"""
REPSVM Tipos de Sentencias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMTipoSentencia(db.Model, UniversalMixin):
    """REPSVMTipoSentencia"""

    # Nombre de la tabla
    __tablename__ = "repsvm_tipos_sentencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    repsvm_agresores = db.relationship("REPSVMAgresor", back_populates="repsvm_tipo_sentencia")

    def __repr__(self):
        """Representación"""
        return f"<REPSVMTipoSentencia {self.nombre}>"
