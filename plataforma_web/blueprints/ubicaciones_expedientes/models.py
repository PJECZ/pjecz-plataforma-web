"""
Ubicaciones de Expedientes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UbicacionExpediente(db.Model, UniversalMixin):
    """ Ubicacion_Expediente """

    UBICACIONES = OrderedDict(
        [
            ("ARCHIVO", "Archivo"),
            ("JUZGADO", "Juzgado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "ubicaciones_expedientes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    expediente = db.Column(db.String(256), nullable=False)
    ubicacion = db.Column(
        db.Enum(*UBICACIONES, name="ubicaciones_opciones", native_enum=False),
        index=True,
        nullable=False,
    )

    def __repr__(self):
        """ Representación """
        return f"<UbicacionExpediente {self.nombre}>"
