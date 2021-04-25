"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Permiso:
    """ Permiso tiene como constantes enteros de potencia dos """

    # Usuarios, Bitácoras, Entradas-Salidas, Roles
    VER_CUENTAS = 0b1
    MODIFICAR_CUENTAS = 0b10
    CREAR_CUENTAS = 0b100

    # Distritos, Autoridades
    VER_CATALOGOS = 0b1000
    MODIFICAR_CATALOGOS = 0b10000
    CREAR_CATALOGOS = 0b100000

    # CID, Tareas, Transcripciones
    VER_ADMINISTRATIVOS = 0b1000000
    MODIFICAR_ADMINISTRATIVOS = 0b10000000
    CREAR_ADMINISTRATIVOS = 0b100000000

    # Abogados registrados, Peritos, Ubicación de expedientes
    VER_CONSULTAS = 0b1000000000
    MODIFICAR_CONSULTAS = 0b10000000000
    CREAR_CONSULTAS = 0b100000000000

    # Agendas, Glosas, Listas de Acuerdos, Sentencias
    VER_JUSTICIABLES = 0b1000000000000
    MODIFICAR_JUSTICIABLES = 0b10000000000000
    CREAR_JUSTICIABLES = 0b100000000000000
    ADMINISTRAR_JUSTICIABLES = 0b1000000000000000

    # Edictos
    VER_NOTARIALES = 0b10000000000000000
    MODIFICAR_NOTARIALES = 0b100000000000000000
    CREAR_NOTARIALES = 0b1000000000000000000
    ADMINISTRAR_NOTARIALES = 0b10000000000000000000

    def __repr__(self):
        """ Representación """
        return "<Permiso>"


class Rol(db.Model, UniversalMixin):
    """ Rol """

    # Nombre de la tabla
    __tablename__ = "roles"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    permiso = db.Column(db.Integer, nullable=False)
    por_defecto = db.Column(db.Boolean, default=False, index=True)

    # Hijos
    usuarios = db.relationship("Usuario", backref="rol")

    def add_permission(self, perm):
        """ Agregar permiso """
        if not self.has_permission(perm):
            self.permiso += perm

    def remove_permission(self, perm):
        """ Retirar permiso """
        if self.has_permission(perm):
            self.permiso -= perm

    def reset_permissions(self):
        """ Poner permisos a cero """
        self.permiso = 0

    def has_permission(self, perm):
        """ ¿Tiene el permiso dado? """
        return self.permiso & perm == perm

    @staticmethod
    def insert_roles():
        """ Insertar roles iniciales """
        roles = {
            "ADMINISTRADOR": [
                Permiso.VER_CUENTAS,
                Permiso.MODIFICAR_CUENTAS,
                Permiso.CREAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.MODIFICAR_CATALOGOS,
                Permiso.CREAR_CATALOGOS,
                Permiso.VER_ADMINISTRATIVOS,
                Permiso.MODIFICAR_ADMINISTRATIVOS,
                Permiso.CREAR_ADMINISTRATIVOS,
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.MODIFICAR_JUSTICIABLES,
                Permiso.CREAR_JUSTICIABLES,
                Permiso.ADMINISTRAR_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.MODIFICAR_NOTARIALES,
                Permiso.CREAR_NOTARIALES,
                Permiso.ADMINISTRAR_NOTARIALES,
            ],
            "SOPORTE TECNICO": [
                Permiso.VER_CUENTAS,
                Permiso.MODIFICAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
            ],
            "JUZGADO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.MODIFICAR_JUSTICIABLES,
                Permiso.CREAR_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
            ],
            "NOTARIA": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.MODIFICAR_NOTARIALES,
                Permiso.CREAR_NOTARIALES,
            ],
            "SECRETARIA TECNICA": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
            ],
            "USUARIO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
            ],
            "OBSERVADOR": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
            ],
        }
        rol_por_defecto = "OBSERVADOR"
        for item in roles:
            rol = Rol.query.filter_by(nombre=item).first()
            if rol is None:
                rol = Rol(nombre=item)
            rol.reset_permissions()
            for perm in roles[item]:
                rol.add_permission(perm)
            rol.por_defecto = rol.nombre == rol_por_defecto
            db.session.add(rol)
        db.session.commit()

    def can_view(self, module):
        """ ¿Tiene permiso para ver? """
        if module in ("bitacoras", "entradas_salidas", "roles", "usuarios"):
            return self.has_permission(Permiso.VER_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.VER_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros", "tareas", "transcripciones"):
            return self.has_permission(Permiso.VER_ADMINISTRATIVOS)
        if module in ("abogados", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.VER_CONSULTAS)
        if module in ("agendas", "glosas", "listas_de_acuerdos"):
            return self.has_permission(Permiso.VER_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.VER_NOTARIALES)
        return False

    def can_insert(self, module):
        """ ¿Tiene permiso para agregar? """
        if module == "usuarios":
            return self.has_permission(Permiso.MODIFICAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.MODIFICAR_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros", "tareas", "transcripciones"):
            return self.has_permission(Permiso.MODIFICAR_ADMINISTRATIVOS)
        if module in ("abogados", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.MODIFICAR_CONSULTAS)
        if module in ("agendas", "glosas", "listas_de_acuerdos"):
            return self.has_permission(Permiso.MODIFICAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.MODIFICAR_NOTARIALES)
        return False

    def can_edit(self, module):
        """ ¿Tiene permiso para editar? """
        if module == "usuarios":
            return self.has_permission(Permiso.CREAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.CREAR_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros", "tareas", "transcripciones"):
            return self.has_permission(Permiso.CREAR_ADMINISTRATIVOS)
        if module in ("abogados", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.CREAR_CONSULTAS)
        if module in ("agendas", "glosas", "listas_de_acuerdos"):
            return self.has_permission(Permiso.CREAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.CREAR_NOTARIALES)
        return False

    def can_admin(self, module):
        """ ¿Tiene permiso para administrar? """
        if module in ("agendas", "glosas", "listas_de_acuerdos"):
            return self.has_permission(Permiso.ADMINISTRAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.ADMINISTRAR_NOTARIALES)
        return False

    def __repr__(self):
        """ Representación """
        return f"<Rol {self.nombre}>"
