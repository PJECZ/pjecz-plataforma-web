"""
Domicilios, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Domicilio(db.Model, UniversalMixin):
    """Domicilio"""

    # Nombre de la tabla
    __tablename__ = "domicilios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    estado = db.Column(db.String(64), nullable=False)
    municipio = db.Column(db.String(64), nullable=False)
    calle = db.Column(db.String(256), nullable=False)
    num_ext = db.Column(db.String(24), nullable=False, default="", server_default="")
    num_int = db.Column(db.String(24), nullable=False, default="", server_default="")
    colonia = db.Column(db.String(256), nullable=False, default="", server_default="")
    cp = db.Column(db.Integer(), nullable=False)
    completo = db.Column(db.String(1024), nullable=False, default="", server_default="")
    numeracion_telefonica = db.Column(db.String(256), nullable=False, default="", server_default="")

    # Hijos
    oficinas = db.relationship("Oficina", back_populates="domicilio")

    def elaborar_completo(self):
        """Elaborar completo"""
        elementos = []
        if self.calle and self.num_ext and self.num_int:
            elementos.append(f"{self.calle} #{self.num_ext}-{self.num_int}")
        elif self.calle and self.num_ext:
            elementos.append(f"{self.calle} #{self.num_ext}")
        elif self.calle:
            elementos.append(self.calle)
        if self.colonia:
            elementos.append(self.colonia)
        if self.municipio:
            elementos.append(self.municipio)
        if self.estado and self.cp > 0:
            elementos.append(f"{self.estado}, C.P. {self.cp}")
        elif self.estado:
            elementos.append(self.estado)
        return ", ".join(elementos)

    def __repr__(self):
        """Representación"""
        return "<Domicilio>"
