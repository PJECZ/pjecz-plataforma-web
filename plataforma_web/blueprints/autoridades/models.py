"""
Autoridades, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Autoridad(db.Model, UniversalMixin):
    """Autoridad"""

    ORGANOS_JURISDICCIONALES = OrderedDict(
        [
            ("NO DEFINIDO", "No Definido"),
            ("JUZGADO DE PRIMERA INSTANCIA", "Juzgado de Primera Instancia"),
            ("JUZGADO DE PRIMERA INSTANCIA ORAL", "Juzgado de Primera Instancia Oral"),
            ("PLENO O SALA DEL TSJ", "Pleno o Sala del TSJ"),
            ("TRIBUNAL DISTRITAL", "Tribunal Distrital"),
            ("TRIBUNAL DE CONCILIACION Y ARBITRAJE", "Tribunal de Conciliación y Arbitraje"),
        ]
    )
    AUDIENCIAS_CATEGORIAS = OrderedDict(
        [
            ("NO DEFINIDO", "No Definido"),
            ("CIVIL FAMILIAR MERCANTIL LETRADO TCYA", "Civil Familiar Mercantil Letrado TCyA"),
            ("MATERIA ACUSATORIO PENAL ORAL", "Materia Acusatorio Penal Oral"),
            ("DISTRITALES", "Distritales"),
            ("SALAS", "Salas"),
        ]
    )
    SEDES = OrderedDict(
        [
            ("ND", "ND"),
            ("DACN", "DACN"),
            ("DMNC", "DMNC"),
            ("DPRR", "DPRR"),
            ("DRGR", "DRGR"),
            ("DSBN", "DSBN"),
            ("DSLT", "DSLT"),
            ("DSPD", "DSPD"),
            ("DTRC", "DTRC"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="autoridades")
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="autoridades")

    # Columnas
    clave = db.Column(db.String(16), nullable=False, unique=True)
    descripcion = db.Column(db.String(256), nullable=False)
    descripcion_corta = db.Column(db.String(64), nullable=False, default="", server_default="")
    es_archivo_solicitante = db.Column(db.Boolean, nullable=False, default=False)
    es_cemasc = db.Column(db.Boolean, nullable=False, default=False)
    es_defensoria = db.Column(db.Boolean, nullable=False, default=False)
    es_extinto = db.Column(db.Boolean, nullable=False, default=False)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)
    es_notaria = db.Column(db.Boolean, nullable=False, default=False)
    es_revisor_escrituras = db.Column(db.Boolean, nullable=False, default=False)
    es_organo_especializado = db.Column(db.Boolean, nullable=False, default=False)
    organo_jurisdiccional = db.Column(db.Enum(*ORGANOS_JURISDICCIONALES, name="tipos_organos_jurisdiccionales", native_enum=False), index=True, nullable=False)
    directorio_edictos = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_glosas = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_listas_de_acuerdos = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_sentencias = db.Column(db.String(256), nullable=False, default="", server_default="")
    audiencia_categoria = db.Column(db.Enum(*AUDIENCIAS_CATEGORIAS, name="tipos_audiencias_categorias", native_enum=False), index=True, nullable=False)
    limite_dias_listas_de_acuerdos = db.Column(db.Integer(), nullable=False, default=0)
    datawarehouse_id = db.Column(db.Integer(), nullable=True)  # Columna para comunicación con SAJI
    sede = db.Column(db.Enum(*SEDES, name="tipos_sedes", native_enum=False), index=True, nullable=False)  # Clave del distrito judicial geografico

    # Hijos
    arc_documentos = db.relationship("ArcDocumento", back_populates="autoridad", lazy="noload")
    arc_remesas = db.relationship("ArcRemesa", back_populates="autoridad", lazy="noload")
    arc_solicitudes = db.relationship("ArcSolicitud", back_populates="autoridad", lazy="noload")
    audiencias = db.relationship("Audiencia", back_populates="autoridad", lazy="noload")
    autoridades_funcionarios = db.relationship("AutoridadFuncionario", back_populates="autoridad")
    cid_areas_autoridades = db.relationship("CIDAreaAutoridad", back_populates="autoridad", lazy="noload")
    cid_procedimientos = db.relationship("CIDProcedimiento", back_populates="autoridad", lazy="noload")
    edictos = db.relationship("Edicto", back_populates="autoridad", lazy="noload")
    est_informes = db.relationship("EstInforme", back_populates="autoridad", lazy="noload")
    glosas = db.relationship("Glosa", back_populates="autoridad", lazy="noload")
    listas_de_acuerdos = db.relationship("ListaDeAcuerdo", back_populates="autoridad", lazy="noload")
    not_conversaciones = db.relationship("NotConversacion", back_populates="autoridad", lazy="noload")
    not_escrituras = db.relationship("NotEscritura", back_populates="autoridad")
    not_mensajes = db.relationship("NotMensaje", back_populates="autoridad", lazy="noload")
    redams = db.relationship("Redam", back_populates="autoridad", lazy="noload")
    req_requisiciones = db.relationship("ReqRequisicion", back_populates="autoridad", lazy="noload")
    sentencias = db.relationship("Sentencia", back_populates="autoridad", lazy="noload")
    siga_grabaciones = db.relationship("SIGAGrabacion", back_populates="autoridad", lazy="noload")
    tesis_jurisprudencias = db.relationship("TesisJurisprudencia", back_populates="autoridad", lazy="noload")
    ubicaciones_expedientes = db.relationship("UbicacionExpediente", back_populates="autoridad", lazy="noload")
    usuarios = db.relationship("Usuario", back_populates="autoridad")  # Mantener sin lazy

    @property
    def nombre(self):
        """Junta clave : descripcion_corta"""
        return self.clave + " : " + self.descripcion_corta

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.clave}>"
