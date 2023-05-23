"""
SIGA Grabaciones, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SIGAGrabacion(db.Model, UniversalMixin):
    """SIGA Grabación"""

    ESTADOS = OrderedDict(
        [
            ("VALIDO", "Válida"),
            ("INVALIDO", "Corrupta en algún tipo de dato"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "siga_grabaciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    siga_sala_id = db.Column(db.Integer, db.ForeignKey("siga_salas.id"), index=True, nullable=False)
    siga_sala = db.relationship("SIGASala", back_populates="siga_grabaciones")
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="siga_grabaciones")
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="siga_grabaciones")

    # Columnas
    expediente = db.Column(db.String(32), nullable=False)
    inicio = db.Column(db.DateTime(), nullable=False)
    termino = db.Column(db.DateTime())
    archivo_nombre = db.Column(db.String(128), nullable=False)
    justicia_ruta = db.Column(db.String(512))
    storage_url = db.Column(db.String(512))
    tamanio = db.Column(db.Integer())
    duracion = db.Column(db.Time())
    transcripcion = db.Column(db.JSON())
    estado = db.Column(db.Enum(*ESTADOS, name="tipos_estados", native_enum=False), index=True, nullable=False)
    nota = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Grabación {self.id}>"
