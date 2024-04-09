"""
Usuarios, modelos
"""

from collections import OrderedDict
from flask import current_app
from flask_login import UserMixin

from lib.universal_mixin import UniversalMixin
from plataforma_web.extensions import db, pwd_context

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol
from plataforma_web.blueprints.modulos_favoritos.models import ModuloFavorito


class Usuario(db.Model, UserMixin, UniversalMixin):
    """Usuario"""

    WORKSPACES = OrderedDict(
        [
            ("BUSINESS STARTED", "Business Started"),
            ("BUSINESS STANDARD", "Business Standard"),
            ("COAHUILA", "Coahuila"),
            ("EXTERNO", "Externo"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "usuarios"

    # Clave primaria
    id = db.Column(db.Integer(), primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="usuarios")
    oficina_id = db.Column(db.Integer, db.ForeignKey("oficinas.id"), index=True, nullable=False)
    oficina = db.relationship("Oficina", back_populates="usuarios")

    # Columnas
    email = db.Column(db.String(256), nullable=False, unique=True, index=True)
    email_personal = db.Column(db.String(256), nullable=False, default="", server_default="")
    nombres = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256), nullable=False)
    apellido_materno = db.Column(db.String(256), nullable=False, default="", server_default="")
    curp = db.Column(db.String(18), nullable=False, default="", server_default="")
    puesto = db.Column(db.String(256), nullable=False, default="", server_default="")
    telefono = db.Column(db.String(48), nullable=False, default="", server_default="")
    telefono_celular = db.Column(db.String(48), nullable=False, default="", server_default="")
    extension = db.Column(db.String(24), nullable=False, default="", server_default="")
    fotografia_url = db.Column(db.String(512), nullable=False, default="", server_default="")
    efirma_registro_id = db.Column(db.Integer, nullable=True)
    workspace = db.Column(db.Enum(*WORKSPACES, name="tipos_workspaces", native_enum=False), index=True, nullable=False)

    # Columnas que no deben ser expuestas
    api_key = db.Column(db.String(128), nullable=False)
    api_key_expiracion = db.Column(db.DateTime(), nullable=False)
    contrasena = db.Column(db.String(256), nullable=False)

    # Hijos
    arc_documentos_bitacoras = db.relationship("ArcDocumentoBitacora", back_populates="usuario", lazy="noload")
    arc_solicitudes_asignado = db.relationship("ArcSolicitud", back_populates="usuario_asignado", lazy="noload")
    arc_solicitudes_bitacoras = db.relationship("ArcSolicitudBitacora", back_populates="usuario", lazy="noload")
    arc_remesas = db.relationship("ArcRemesa", back_populates="usuario_asignado", lazy="noload")
    arc_remesas_bitacoras = db.relationship("ArcRemesaBitacora", back_populates="usuario", lazy="noload")
    bitacoras = db.relationship("Bitacora", back_populates="usuario", lazy="noload")
    cid_procedimientos = db.relationship("CIDProcedimiento", back_populates="usuario", lazy="noload")
    entradas_salidas = db.relationship("EntradaSalida", back_populates="usuario", lazy="noload")
    fin_vales = db.relationship("FinVale", back_populates="usuario", lazy="noload")
    inv_custodias = db.relationship("InvCustodia", back_populates="usuario", lazy="noload")
    modulos_favoritos = db.relationship("ModuloFavorito", back_populates="usuario")
    req_requisiciones = db.relationship("ReqRequisicion", back_populates="usuario", lazy="noload")
    soportes_tickets = db.relationship("SoporteTicket", back_populates="usuario", lazy="noload")
    tareas = db.relationship("Tarea", back_populates="usuario", lazy="noload")
    usuarios_datos = db.relationship("UsuarioDato", back_populates="usuario")  # Sin lazy="noload" para que funcione el menu
    usuarios_roles = db.relationship("UsuarioRol", back_populates="usuario")  # Sin lazy="noload" para que funcione el menu
    usuarios_nominas = db.relationship("UsuarioNomina", back_populates="usuario", lazy="noload")
    usuarios_solicitudes = db.relationship("UsuarioSolicitud", back_populates="usuario", lazy="noload")

    # Propiedades
    modulos_menu_principal_consultados = []
    modulos_favoritos_menu_principal_consultados = []
    permisos_consultados = {}

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    @property
    def modulos_menu_principal(self):
        """Elaborar listado con los modulos ordenados para el menu principal"""
        if len(self.modulos_menu_principal_consultados) > 0:
            return self.modulos_menu_principal_consultados
        modulos_favoritos_query = ModuloFavorito.query.filter(ModuloFavorito.estatus == "A").filter(ModuloFavorito.usuario_id == self.id).all()
        modulos_favoritos_coleccion = []
        for modulo in modulos_favoritos_query:
            modulos_favoritos_coleccion.append(modulo.modulo_id)
        modulos_favoritos = []
        modulos = []
        modulos_nombres = []
        for usuario_rol in self.usuarios_roles:
            if usuario_rol.estatus == "A":
                for permiso in usuario_rol.rol.permisos:
                    if permiso.modulo.nombre not in modulos_nombres and permiso.estatus == "A" and permiso.nivel > 0 and permiso.modulo.en_navegacion:
                        modulos.append(permiso.modulo)
                        modulos_nombres.append(permiso.modulo.nombre)
                        if permiso.modulo.id in modulos_favoritos_coleccion:
                            modulos_favoritos.append(permiso.modulo)
        self.modulos_favoritos_menu_principal_consultados = sorted(modulos_favoritos, key=lambda x: x.nombre_corto)
        self.modulos_menu_principal_consultados = sorted(modulos, key=lambda x: x.nombre_corto)
        return self.modulos_menu_principal_consultados

    @property
    def modulos_favoritos_menu_principal(self):
        """Entrega el listado con los modulos favoritos ordenados para el menu principal"""
        return self.modulos_favoritos_menu_principal_consultados

    @property
    def permisos(self):
        """Entrega un diccionario con todos los permisos"""
        if len(self.permisos_consultados) > 0:
            return self.permisos_consultados
        self.permisos_consultados = {}
        for usuario_rol in self.usuarios_roles:
            if usuario_rol.estatus == "A":
                for permiso in usuario_rol.rol.permisos:
                    if permiso.estatus == "A":
                        etiqueta = permiso.modulo.nombre
                        if etiqueta not in self.permisos_consultados or permiso.nivel > self.permisos_consultados[etiqueta]:
                            self.permisos_consultados[etiqueta] = permiso.nivel
        return self.permisos_consultados

    @classmethod
    def find_by_identity(cls, identity):
        """Encontrar a un usuario por su correo electrónico"""
        return Usuario.query.filter(Usuario.email == identity).first()

    @property
    def is_active(self):
        """¿Es activo?"""
        return self.estatus == "A"

    def authenticated(self, with_password=True, password=""):
        """Ensure a user is authenticated, and optionally check their password."""
        if self.id and with_password:
            return pwd_context.verify(password, self.contrasena)
        return True

    def can(self, modulo_nombre: str, permission: int):
        """¿Tiene permiso?"""
        if modulo_nombre in self.permisos:
            return self.permisos[modulo_nombre] >= permission
        return False

    def can_view(self, modulo_nombre: str):
        """¿Tiene permiso para ver?"""
        return self.can(modulo_nombre, Permiso.VER)

    def can_edit(self, modulo_nombre: str):
        """¿Tiene permiso para editar?"""
        return self.can(modulo_nombre, Permiso.MODIFICAR)

    def can_insert(self, modulo_nombre: str):
        """¿Tiene permiso para agregar?"""
        return self.can(modulo_nombre, Permiso.CREAR)

    def can_admin(self, modulo_nombre: str):
        """¿Tiene permiso para administrar?"""
        return self.can(modulo_nombre, Permiso.ADMINISTRAR)

    def launch_task(self, comando, mensaje, *args, **kwargs):
        """Lanzar tarea en el fondo"""
        rq_job = current_app.task_queue.enqueue(f"plataforma_web.blueprints.{comando}", *args, **kwargs)
        tarea = Tarea(id=rq_job.get_id(), comando=comando, mensaje=mensaje, usuario=self)
        tarea.save()
        return tarea

    def get_tasks_in_progress(self):
        """Obtener tareas"""
        return Tarea.query.filter_by(usuario=self, ha_terminado=False).all()

    def get_task_in_progress(self, nombre):
        """Obtener progreso de una tarea"""
        return Tarea.query.filter_by(nombre=nombre, usuario=self, ha_terminado=False).first()

    def get_roles(self):
        """Obtener roles"""
        usuarios_roles = UsuarioRol.query.filter_by(usuario_id=self.id).filter_by(estatus="A").all()
        return [usuario_rol.rol.nombre for usuario_rol in usuarios_roles]

    def __repr__(self):
        """Representación"""
        return f"<Usuario {self.email}>"
