"""
Documentos SIBED, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SIBED_Documento(db.Model, UniversalMixin):
    """Documento SIBED"""

    TIPOS = OrderedDict(  # varchar(16)
        [
            ("NO DEFINIDO", "No Definido"),
            ("CUADERNILLO", "Cuadernillo"),
            ("ENCOMIENDA", "Encomienda"),
            ("EXHORTO", "Exhorto"),
            ("EXPEDIENTE", "Expediente"),
            ("EXPEDIENTILLO", "Expedientillo"),
            ("FOLIO", "Folio"),
            ("LIBRO", "Libro"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "sibed_documentos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    actor = db.Column(db.String(256), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    demandado = db.Column(db.String(256))
    expediente = db.Column(db.String(16), index=True, nullable=False)  # dígitos/YYYY-XXX
    juicio = db.Column(db.String(128))
    juzgado_id = db.Column(db.Integer, nullable=False)
    fojas = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.String(256))
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )

    def __repr__(self):
        """Representación"""
        return f"<Documento SIBED> {self.id}"
