"""
CID Procedimientos, modelos
"""
from collections import OrderedDict
import hashlib

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDProcedimiento(db.Model, UniversalMixin):
    """CIDProcedimiento"""

    SEGUIMIENTOS = OrderedDict(
        [
            ("EN ELABORACION", "En Elaboración"),
            ("FIRMADO", "Firmado"),
            ("ACEPTADO", "Aprobado"),
            ("RECHAZADO", "Rechazado"),
            ("CANCELADO", "Cancelado"),
            ("ARCHIVADO", "Archivado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="cid_procedimientos")

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

    # Número en la cadena, empieza en cero cuando quien elabora aun no lo firma
    cadena = db.Column(db.Integer(), nullable=False)

    # Seguimiento
    seguimiento = db.Column(
        db.Enum(*SEGUIMIENTOS, name="cid_procedimientos_seguimientos", native_enum=False),
        index=True,
        nullable=False,
    )

    # ID del registro anterior en la cadena
    anterior_id = db.Column(db.Integer(), nullable=False)

    # Al firmarse cambia de texto vacio al hash MD5 y ya no debe modificarse
    firma = db.Column(db.String(32), nullable=False, default="", server_default="")

    # Al elaborar el archivo PDF y subirlo a Google Storage
    archivo = db.Column(db.String(256), default="", server_default="")
    url = db.Column(db.String(512), default="", server_default="")

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def archivo_pdf(self):
        """Nombre del archivo PDF"""
        if self.id is None or self.creado is None:
            raise ValueError("No se puede definir el nombre del archivo PDF porque no se ha guardado o consultado")
        # Tiempo + ID Hash
        return self.creado.strftime("%Y%m%d-%H%M%S") + "-" + self.encode_id() + ".pdf"

    def elaborar_firma(self):
        """Generate a hash representing the current sample state"""
        if self.id is None or self.creado is None:
            raise ValueError("No se puede elaborar la firma porque no se ha guardado o consultado")
        elementos = []
        elementos.append(str(self.id))
        elementos.append(self.creado.strftime("%Y-%m-%d %H:%M:%S"))
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
        return hashlib.md5("|".join(elementos).encode("utf-8")).hexdigest()

    def __repr__(self):
        """Representación"""
        return "<CIDProcedimiento>"
