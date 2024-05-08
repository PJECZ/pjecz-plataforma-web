"""
Exh Exhortos Archivos
"""

from sqlalchemy.sql import func

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

    # Hash SHA256 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo.
    hash_sha256 = db.Column(db.String(256))

    # Identificador del tipo de documento que representa el archivo:
    # 1 = Oficio
    # 2 = Acuerdo
    # 3 = Anexo
    tipo_documento = db.Column(db.Integer, nullable=False)

    # URL del archivo en Google Storage
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    # Estado de recepción del documento
    estado = db.Column(db.Enum(*ESTADOS, name="exh_exhortos_archivos_estados", native_enum=False), nullable=True)

    # Tamaño del archivo recibido en bytes
    tamano = db.Column(db.Integer, nullable=False)

    # Fecha y hora de recepción del documento
    fecha_hora_recepcion = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoArchivo {self.id}>"
