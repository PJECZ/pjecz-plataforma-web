"""
Bitácoras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Bitacora(db.Model, UniversalMixin):
    """Bitacora"""

    MODULOS = OrderedDict(
        [
            ("ABOGADOS", "Abogados"),
            ("AUDIENCIAS", "Audiencias"),
            ("AUTORIDADES", "Autoridades"),
            ("DOCUMENTACIONES", "Documentaciones"),
            ("DISTRITOS", "Distritos"),
            ("EDICTOS", "Edictos"),
            ("GLOSAS", "Glosas"),
            ("LISTAS DE ACUERDOS", "Listas de Acuerdos"),
            ("MATERIAS", "Materias"),
            ("MATERIAS TIPOS JUICIOS", "Materias Tipos Juicios"),
            ("PERITOS", "Peritos"),
            ("REPORTES", "Reportes"),
            ("SENTENCIAS", "Sentencias"),
            ("TRANSCRIPCIONES", "Transcripciones"),
            ("UBICACIONES DE EXPEDIENTES", "Ubicaciones de Expedientes"),
            ("USUARIOS", "Usuarios"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="bitacoras")

    # Columnas
    modulo = db.Column(
        db.Enum(*MODULOS, name="tipos_modulos", native_enum=False),
        index=True,
        nullable=False,
    )
    descripcion = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<Bitacora {self.creado} {self.descripcion}>"
