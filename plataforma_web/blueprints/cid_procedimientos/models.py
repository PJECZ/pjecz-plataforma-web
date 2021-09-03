"""
CID Procedimientos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDProcedimiento(db.Model, UniversalMixin):
    """CIDProcedimiento"""

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="cid_procedimientos")

    # Columnas
    titulo_procedimiento = db.Column(db.String(256), nullable=False)
    codigo = db.Column(db.String(16), nullable=False)
    revision = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    objetivo = db.Column(db.Text())
    alcance = db.Column(db.Text())
    documentos = db.Column(db.Text())
    definiciones = db.Column(db.Text())
    responsabilidades = db.Column(db.Text())
    desarrollo = db.Column(db.Text())
    registros = db.Column(db.Text())
    elaboro_nombre = db.Column(db.String(256))
    elaboro_puesto = db.Column(db.String(256))
    elaboro_email = db.Column(db.String(256))
    reviso_nombre = db.Column(db.String(256))
    reviso_puesto = db.Column(db.String(256))
    reviso_email = db.Column(db.String(256))
    aprobo_nombre = db.Column(db.String(256))
    aprobo_puesto = db.Column(db.String(256))
    aprobo_email = db.Column(db.String(256))
    control_cambios = db.Column(db.Text())

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def __repr__(self):
        """Representación"""
        return "<CIDProcedimiento>"
