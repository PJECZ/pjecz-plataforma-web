"""
Cit Citas Expedientes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CitCitaExpediente(db.Model, UniversalMixin):
    """CitCitaExpediente"""

    # Nombre de la tabla
    __tablename__ = "cit_citas_expedientes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    cit_cita_id = db.Column(db.Integer, db.ForeignKey('cit_citas.id'), index=True, nullable=False)
    cit_cita = db.relationship('CitCita', back_populates='cit_citas_expedientes')

    # Columnas
    expediente = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<CitCitaExpediente>"
