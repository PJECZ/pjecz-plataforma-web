"""
CID Formatos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDFormato(db.Model, UniversalMixin):
    """ CIDFormato """

    FORMAS = OrderedDict(
        [
            ("ELECTRONICO", "Electrónico"),
            ("PAPEL", "Papel"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "cid_formatos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    procedimiento_id = db.Column(db.Integer, db.ForeignKey('cid_procedimientos.id'), index=True, nullable=False)
    procedimiento = db.relationship('CIDProcedimiento', back_populates='formatos')

    # Columnas
    numero = db.Column(db.Integer(), nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    codigo = db.Column(db.String(16), nullable=False)
    responsable = db.Column(db.String(128), nullable=False)
    forma = db.Column(
        db.Enum(*FORMAS, name="etapas", native_enum=False),
        index=True,
        nullable=False,
    )
    tiempo_retencion = db.Column(db.String(48), nullable=False)

    # Hijos
    registros = db.relationship('CIDRegistro', back_populates='formato')

    def __repr__(self):
        """ Representación """
        return "<CIDFormato>"
