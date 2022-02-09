"""
Oficinas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Oficina(db.Model, UniversalMixin):
    """Oficina"""

    # Nombre de la tabla
    __tablename__ = "oficinas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    domicilio_id = db.Column(db.Integer, db.ForeignKey("domicilios.id"), index=True, nullable=False)
    domicilio = db.relationship("Domicilio", back_populates="oficinas")
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="oficinas")

    # Columnas
    clave = db.Column(db.String(32), unique=True, nullable=False)
    descripcion = db.Column(db.String(512), nullable=False)
    descripcion_corta = db.Column(db.String(64))
    es_juridiccional = db.Column(db.Boolean(), nullable=False)
    apertura = db.Column(db.Time(), nullable=False)
    cierre = db.Column(db.Time(), nullable=False)
    limite_personas = db.Column(db.Integer())

    # Hijos
    cit_citas = db.relationship('CitCita', back_populates='oficina', lazy='noload')

    def __repr__(self):
        """Representación"""
        return f"<Oficina> {self.clave}"
