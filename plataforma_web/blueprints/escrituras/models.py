"""
Escrituras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Escritura(db.Model, UniversalMixin):
    """Escritura"""

    TIPOS = OrderedDict(
        [
            ("NORMAL", "Normal"),
            ("ALTERNATIVO", "Alternativo"),
        ]
    )
    ETAPAS = OrderedDict(
        [
            ("PRIMERA", "Primera"),
            ("SEGUNDA", "Segunda"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "escrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="escrituras")

    # Columnas
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    aprobacion_fecha = db.Column(db.Date())
    envio_fecha = db.Column(db.Date(), nullable=False)
    etapa = db.Column(db.Enum(*ETAPAS, name="etapas", native_enum=False), index=True, nullable=False)
    expediente = db.Column(db.String(16), nullable=False, default="", server_default="")
    observaciones = db.Column(db.String(256), nullable=False, default="", server_default="")
    tipo = db.Column(db.Enum(*TIPOS, name="tipos", native_enum=False), index=True, nullable=False)
    texto = db.Column(db.Text(), nullable=False)
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return "<Escritura>"
