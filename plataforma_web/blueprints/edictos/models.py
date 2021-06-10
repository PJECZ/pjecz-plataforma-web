"""
Edictos, modelos

La tabla edictos tiene opcionales los campos expediente y numero_publicacion.

Flask con SQLAlchemy están creando las columnas que permiten valores NULOS.

Una columna string con valor nulo ¡¡¡truena con FastAPI!!!

    DESCRIBE edictos;

    | expediente         | varchar(16)  | YES  |     | NULL
    | numero_publicacion | varchar(16)  | YES  |     | NULL

    UPDATE edictos SET expediente='' WHERE expediente IS NULL;
    ALTER TABLE edictos MODIFY expediente varchar(16) NOT NULL DEFAULT "";

    UPDATE edictos SET numero_publicacion='' WHERE numero_publicacion IS NULL;
    ALTER TABLE edictos MODIFY numero_publicacion varchar(16) NOT NULL DEFAULT "";

    DESCRIBE edictos;

    | expediente         | varchar(16)  | NO   |     |
    | numero_publicacion | varchar(16)  | NO   |     |

"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

SUBDIRECTORIO = "Edictos"


class Edicto(db.Model, UniversalMixin):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="edictos")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), nullable=False, default="")
    numero_publicacion = db.Column(db.String(16), nullable=False, default="")
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.descripcion}>"

    @property
    def ruta(self):
        """Ruta para guardar el archivo"""
