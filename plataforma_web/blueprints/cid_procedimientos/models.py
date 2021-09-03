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
    objetivo = db.Column(db.Text(), nullable=False)
    alcance = db.Column(db.Text(), nullable=False)
    documentos = db.Column(db.Text(), nullable=False)
    definiciones = db.Column(db.Text(), nullable=False)
    responsabilidades = db.Column(db.Text(), nullable=False)
    desarrollo = db.Column(db.Text(), nullable=False)
    registros = db.Column(db.Text(), nullable=False)
    control_cambios = db.Column(db.Text(), nullable=False)
    elaboro_nombre = db.Column(db.Text(), nullable=False)
    elaboro_puesto = db.Column(db.Text(), nullable=False)
    elaboro_email = db.Column(db.Text(), nullable=False)
    reviso_nombre = db.Column(db.Text(), nullable=False)
    reviso_puesto = db.Column(db.Text(), nullable=False)
    reviso_email = db.Column(db.Text(), nullable=False)
    aprobo_nombre = db.Column(db.Text(), nullable=False)
    aprobo_puesto = db.Column(db.Text(), nullable=False)
    aprobo_email = db.Column(db.Text(), nullable=False)

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def __repr__(self):
        """Representación"""
        return "<CIDProcedimiento>"
