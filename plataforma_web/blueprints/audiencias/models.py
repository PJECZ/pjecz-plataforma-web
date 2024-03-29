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
            ("NO DEFINIDO", "No definido"),
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
    tipo_audiencia = db.Column(db.String(256), nullable=False)

    # Columnas para Materias C F M L D(CyF) Salas (CyF) TCyA
    expediente = db.Column(db.String(64), nullable=False, default="", server_default="")
    actores = db.Column(db.String(256), nullable=False, default="", server_default="")
    demandados = db.Column(db.String(256), nullable=False, default="", server_default="")

    # Columnas para Materia Acusatorio Penal Oral
    sala = db.Column(db.String(256), nullable=False, default="", server_default="")
    caracter = db.Column(
        db.Enum(*CARACTERES, name="tipos_caracteres", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    causa_penal = db.Column(db.String(256), nullable=False, default="", server_default="")
    delitos = db.Column(db.String(256), nullable=False, default="", server_default="")

    # Columnas para Distritales Penales
    toca = db.Column(db.String(256), nullable=False, default="", server_default="")
    expediente_origen = db.Column(db.String(256), nullable=False, default="", server_default="")
    imputados = db.Column(db.String(256), nullable=False, default="", server_default="")

    # Columnas para Salas Penales
    # toca
    # expediente_origen
    # delitos
    origen = db.Column(db.String(256), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return "<Audiencia>"
