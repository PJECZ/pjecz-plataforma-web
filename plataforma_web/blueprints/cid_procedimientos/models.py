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

    # Columnas
    titulo_procedimiento = db.Column(db.String(256), nullable=False)  # Título del Procedimiento
    codigo = db.Column(db.String(16), nullable=False)
    revision = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.Date(), nullable=False)  # Fecha Elaboración
    objetivo = db.Column(db.Text(), nullable=False)  # OBJETIVO
    alcance = db.Column(db.Text(), nullable=False)  # ALCANCE
    documentos = db.Column(db.Text(), nullable=False)  # DOCUMENTOS DE REFERENCIA
    definiciones = db.Column(db.Text(), nullable=False)  # DEFINICIONES
    responsabilidades = db.Column(db.Text(), nullable=False)  # RESPONSABILIDADES
    desarrollo = db.Column(db.Text(), nullable=False)  # DESARROLLO
    registros = db.Column(db.Text(), nullable=False)  # REGISTROS
    cambios = db.Column(db.Text(), nullable=False)  # CAMBIOS
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
