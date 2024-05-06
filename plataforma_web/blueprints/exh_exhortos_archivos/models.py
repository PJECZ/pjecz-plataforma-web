"""
Exh Exhortos Archivos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ExhExhortoArchivo(db.Model, UniversalMixin):
    """Exhorto Archivo"""

    ESTADOS = {
        "PENDIENTE": "Pendiente",
        "RECIBIDO": "Recibido",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_archivos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    exh_exhorto_id = db.Column(db.Integer, db.ForeignKey("exh_exhortos.id"), index=True, nullable=False)
    exh_exhorto = db.relationship("ExhExhorto", back_populates="exh_exhortos_archivos")

    # Nombre del archivo, como se enviará. Este debe incluir el la extensión del archivo.
    nombre_archivo = db.Column(db.String(256), nullable=False)

    # Hash SHA1 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo.
    hash_sha1 = db.Column(db.String(256))

    # Hash SHA256 en hexadecimal que corresponde al archivo a recibir. Esto apra comprobar la integridad del archivo.
    hash_sha256 = db.Column(db.String(256))

    # Identificador del tipo de documento que representa el archivo:
    # 1 = Oficio
    # 2 = Acuerdo
    # 3 = Anexo
    tipo_documento = db.Column(db.Integer, nullable=False)

    # URL del archivo en Google Storage
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    estado = db.Column(db.Enum(*ESTADOS, name="exh_exhortos_archivos_estados", native_enum=False), nullable=True)

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoArchivo {self.id}>"
