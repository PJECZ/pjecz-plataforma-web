"""
Usuarios, modelos
"""
from collections import OrderedDict
from flask import current_app
from flask_login import UserMixin

from lib.universal_mixin import UniversalMixin
from plataforma_web.extensions import db, pwd_context

from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.tareas.models import Tarea


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

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="usuarios")

    # Columnas
    email = db.Column(db.String(256), nullable=False, unique=True, index=True)
    contrasena = db.Column(db.String(256), nullable=False)
    nombres = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256), nullable=False)
    apellido_materno = db.Column(db.String(256), default="", server_default="")
    curp = db.Column(db.String(256), default="", server_default="")
    puesto = db.Column(db.String(256), default="", server_default="")
    telefono_celular = db.Column(db.String(256), default="", server_default="")
    workspace = db.Column(db.Enum(*WORKSPACES, name="tipos_workspaces", native_enum=False), index=True, nullable=False)

    # Hijos
    bitacoras = db.relationship("Bitacora", back_populates="usuario", lazy="noload")
    cid_procedimientos = db.relationship("CIDProcedimiento", back_populates="usuario", lazy="noload")
    entradas_salidas = db.relationship("EntradaSalida", back_populates="usuario", lazy="noload")
    tareas = db.relationship("Tarea", back_populates="usuario", lazy="noload")
    usuarios_roles = db.relationship("UsuarioRol", back_populates="usuario")

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

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

    def modulos(self):
        """Elaborar listado con modulos para el menu principal"""
        modulos = []
        modulos_nombres = []
        for usuario_rol in self.usuarios_roles:
            if usuario_rol.estatus == "A":
                for permiso in usuario_rol.rol.permisos:
                    if permiso.estatus == "A" and permiso.nivel > 0 and permiso.modulo.en_navegacion and permiso.modulo.nombre not in modulos_nombres:
                        modulos.append(permiso.modulo)
                        modulos_nombres.append(permiso.modulo.nombre)
        return sorted(modulos, key=lambda x: x.nombre_corto)

    def can(self, module, permission):
        """¿Tiene permiso?"""
        if isinstance(module, str):
            modulo = Modulo.query.filter_by(nombre=module.upper()).filter_by(estatus="A").first()
            if modulo is None:
                return False
        elif isinstance(module, Modulo) is False:
            return False
        maximo = 0
        for usuario_rol in self.usuarios_roles:
            if usuario_rol.estatus == "A":
                for permiso in usuario_rol.rol.permisos:
                    if permiso.estatus == "A" and permiso.modulo == modulo and permiso.nivel > maximo:
                        maximo = permiso.nivel
        return maximo >= permission

    def can_view(self, module):
        """¿Tiene permiso para ver?"""
        return self.can(module, Permiso.VER)

    def can_edit(self, module):
        """¿Tiene permiso para editar?"""
        return self.can(module, Permiso.MODIFICAR)

    def can_insert(self, module):
        """¿Tiene permiso para agregar?"""
        return self.can(module, Permiso.CREAR)

    def can_admin(self, module):
        """¿Tiene permiso para administrar?"""
        return self.can(module, Permiso.ADMINISTRAR)

    def launch_task(self, nombre, descripcion, *args, **kwargs):
        """Arrancar tarea"""
        rq_job = current_app.task_queue.enqueue("plataforma_web.blueprints." + nombre, *args, **kwargs)
        tarea = Tarea(id=rq_job.get_id(), nombre=nombre, descripcion=descripcion, usuario=self)
        tarea.save()
        return tarea

    def get_tasks_in_progress(self):
        """Obtener tareas"""
        return Tarea.query.filter_by(usuario=self, ha_terminado=False).all()

    def get_task_in_progress(self, nombre):
        """Obtener progreso de una tarea"""
        return Tarea.query.filter_by(nombre=nombre, usuario=self, ha_terminado=False).first()

    def __repr__(self):
        """Representación"""
        return f"<Usuario {self.email}>"
