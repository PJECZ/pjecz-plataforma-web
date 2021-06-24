"""
Adiencias, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Audiencia(db.Model, UniversalMixin):
    """Audiencia"""

    CARACTERES = OrderedDict(
        [
            ("PUBLICA", "Pública"),
            ("PRIVADA", "Privada"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "audiencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="audiencias")

    # Columnas comunes
    tiempo = db.Column(db.DateTime, nullable=False)
    tipo_audiencia = db.Column(db.String(256))

    # Columnas para Materias C F M L D(CyF) Salas (CyF) TCyA
    expediente = db.Column(db.String(16))
    actores = db.Column(db.String(256))
    demandados = db.Column(db.String(256))

    # Columnas para Materia Acusatorio Penal Oral
    sala = db.Column(db.String(256))
    caracter = db.Column(
        db.Enum(*CARACTERES, name="tipos_caracteres", native_enum=False),
        index=True,
        nullable=True,
    )
    causa_penal = db.Column(db.String(256))
    delitos = db.Column(db.String(256))

    # Columnas para Distritales Penales y Salas Penales
    toca = db.Column(db.String(256))
    expediente_origen = db.Column(db.String(256))
    # delitos
    imputados = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return "<Audiencia>"
