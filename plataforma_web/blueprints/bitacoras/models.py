"""
Bitácoras, modelos

En MariaDB para agregar las nuevas columnas modulo y url

    ALTER TABLE bitacoras ADD COLUMN modulo varchar(64) NOT NULL;
    ALTER TABLE bitacoras ADD COLUMN url varchar(512) NOT NULL DEFAULT '';
    CREATE INDEX ix_bitacoras_modulo ON bitacoras(modulo);

Verifique con

    SHOW INDEX FROM bitacoras;
    DESCRIBE bitacoras;

"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Bitacora(db.Model, UniversalMixin):
    """Bitacora"""

    MODULOS = OrderedDict(
        [
            ("ABOGADOS", "Abogados"),
            ("AUTORIDADES", "Autoridades"),
            ("DISTRITOS", "Distritos"),
            ("EDICTOS", "Edictos"),
            ("GLOSAS", "Glosas"),
            ("LISTAS DE ACUERDOS", "Listas de Acuerdos"),
            ("MATERIAS", "Materias"),
            ("PERITOS", "Peritos"),
            ("SENTENCIAS", "Sentencias"),
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
