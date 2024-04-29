"""
Exh Exhortos
"""

from sqlalchemy.sql import func

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class ExhExhorto(db.Model, UniversalMixin):
    """Exhorto Exhorto"""

    # Nombre de la tabla
    __tablename__ = "exh_exhortos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # UUID identificador con el que el PJ exhortante identifica el exhorto que envía
    exhorto_origen_id = db.Column(db.String(64), nullable=False, unique=True)

    # Identificador INEGI del Municipio del Estado del PJ exhortado al que se quiere enviar el Exhorto
    # municipio_destino_id = db.Column(db.Integer, db.ForeignKey("municipios.id"), index=True, nullable=False)
    # municipio_destino = db.relationship("Municipio", back_populates="exh_exhortos_destinos")

    # Clave de la materia (el que se obtuvo en la consulta de materias del PJ exhortado) al que el Exhorto hace referencia
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="exh_exhortos")

    # Identificador INEGI del Estado de origen del Municipio donde se ubica el Juzgado del PJ exhortante
    # estado_origen_id = Column(Integer, ForeignKey("estados.id"), index=True, nullable=False)
    # estado_origen = relationship("Estado", back_populates="exhortos")

    # Identificador INEGI del Municipio donde está localizado el Juzgado del PJ exhortante
    municipio_origen_id = db.Column(db.Integer, db.ForeignKey("municipios.id"), index=True, nullable=False)
    municipio_origen = db.relationship("Municipio", back_populates="exh_exhortos_origenes")

    # Identificador propio del Juzgado/Área que envía el Exhorto
    juzgado_origen_id = db.Column(db.String(64))
    # Nombre del Juzgado/Área que envía el Exhorto
    juzgado_origen_nombre = db.Column(db.String(256), nullable=False)
    # El número de expediente (o carpeta procesal, carpeta...) que tiene el asunto en el Juzgado de Origen
    numero_expediente_origen = db.Column(db.String(256), nullable=False)
    numero_oficio_origen = db.Column(db.String(256))
    tipo_juicio_asunto_delitos = db.Column(db.String(256), nullable=False)
    juez_exhortante = db.Column(db.String(256))
    fojas = db.Column(db.Integer, nullable=False)
    dias_responder = db.Column(db.Integer, nullable=False)
    tipo_diligenciacion_nombre = db.Column(db.String(256))
    fecha_origen = db.Column(db.DateTime, server_default=func.now())
    observaciones = db.Column(db.String(1024))

    # Hijos
    # partes                    PersonaParte[] NO
    exh_exhortos_partes = db.relationship('ExhExhortoParte', back_populates='exh_exhorto', lazy='noload')
    # archivos                  ArchivoARecibir[] SI
    exh_exhortos_archivos = db.relationship('ExhExhortoArchivo', back_populates='exh_exhorto', lazy='noload')
    
    def __repr__(self):
        """Representación"""
        return f"<Exhorto {self.id}>"