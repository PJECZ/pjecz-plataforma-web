"""
Exhortos Archivos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class ExhArchivo(db.Model, UniversalMixin):
    """Exhorto Archivo"""

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_archivos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombreArchivo = db.Column(db.String(256), nullable=False)
    hashSha1 = db.Column(db.String(256))
    hashSha256 = db.Column(db.String(256))
    tipoDocumento = db.Column(db.Integer(), nullable=False) # 1=Oficio, 2=Acuerdo, 3=Anexo

    def __repr__(self):
        """Representación"""
        return f"<ExhArchivo {self.nombreArchivo}>"