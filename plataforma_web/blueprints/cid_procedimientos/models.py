"""
CID Procedimientos, modelos
"""
import hashlib

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDProcedimiento(db.Model, UniversalMixin):
    """CIDProcedimiento"""

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="cid_procedimientos")

    # Columnas
    titulo_procedimiento = db.Column(db.String(256), nullable=False)
    codigo = db.Column(db.String(16), nullable=False)
    revision = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    objetivo = db.Column(db.JSON())
    alcance = db.Column(db.JSON())
    documentos = db.Column(db.JSON())
    definiciones = db.Column(db.JSON())
    responsabilidades = db.Column(db.JSON())
    desarrollo = db.Column(db.JSON())
    registros = db.Column(db.JSON())
    elaboro_nombre = db.Column(db.String(256), nullable=False, default="", server_default="")
    elaboro_puesto = db.Column(db.String(256), nullable=False, default="", server_default="")
    elaboro_email = db.Column(db.String(256), nullable=False, default="", server_default="")
    reviso_nombre = db.Column(db.String(256), nullable=False, default="", server_default="")
    reviso_puesto = db.Column(db.String(256), nullable=False, default="", server_default="")
    reviso_email = db.Column(db.String(256), nullable=False, default="", server_default="")
    aprobo_nombre = db.Column(db.String(256), nullable=False, default="", server_default="")
    aprobo_puesto = db.Column(db.String(256), nullable=False, default="", server_default="")
    aprobo_email = db.Column(db.String(256), nullable=False, default="", server_default="")
    control_cambios = db.Column(db.JSON())
    firma = db.Column(db.String(1024))

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def elaborar_firma(self):
        """Generate a hash representing the current sample state"""
        if self.id is None or self.creado is None:
            raise ValueError("No se puede elaborar la firma porque no se ha guardado o consultado")
        elementos = []
        elementos.append(self.creado.strftime("%Y-%m-%d %H:%M:%S"))
        elementos.append(str(self.id))
        elementos.append(self.titulo_procedimiento)
        elementos.append(self.codigo)
        elementos.append(str(self.revision))
        elementos.append(str(self.objetivo))
        elementos.append(str(self.alcance))
        elementos.append(str(self.documentos))
        elementos.append(str(self.definiciones))
        elementos.append(str(self.responsabilidades))
        elementos.append(str(self.desarrollo))
        elementos.append(str(self.registros))
        elementos.append(self.elaboro_email)
        elementos.append(self.reviso_email)
        elementos.append(self.aprobo_email)
        elementos.append(str(self.control_cambios))
        firma = hashlib.md5("|".join(elementos).encode("utf-8"))
        return firma.hexdigest()

    def validar_firma(self, validar_esta_firma):
        """Probar firma electronica"""
        return validar_esta_firma == self.firma

    def __repr__(self):
        """Representación"""
        return "<CIDProcedimiento>"
