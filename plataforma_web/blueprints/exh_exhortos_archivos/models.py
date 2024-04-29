"""
Exh Exhortos Archivos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class ExhExhortoArchivo(db.Model, UniversalMixin):
    """Exhorto Archivo"""

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_archivos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    exh_exhorto_id = db.Column(db.Integer, db.ForeignKey('exh_exhortos.id'), index=True, nullable=False)
    exh_exhorto = db.relationship('ExhExhorto', back_populates='exh_exhortos_archivos')

    # Columnas
    nombre_archivo = db.Column(db.String(256), nullable=False)
    hash_sha1 = db.Column(db.String(256))
    hash_sha256 = db.Column(db.String(256))
    tipo_documento = db.Column(db.Integer(), nullable=False) # 1=Oficio, 2=Acuerdo, 3=Anexo

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoArchivo {self.nombre_archivo}>"