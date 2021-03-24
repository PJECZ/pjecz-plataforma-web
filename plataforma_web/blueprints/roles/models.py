"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Permiso:
    """ Permiso tiene como constantes enteros de potencia dos """

    VER_CUENTAS = 1
    MODIFICAR_CUENTAS = 2
    CREAR_CUENTAS = 4

    VER_CATALOGOS = 8
    MODIFICAR_CATALOGOS = 16
    CREAR_CATALOGOS = 32

    VER_CONTENIDOS = 64
    MODIFICAR_CONTENIDOS = 128
    CREAR_CONTENIDOS = 256

    VER_ABOGADOS = 512
    MODIFICAR_ABOGADOS = 1024
    CREAR_ABOGADOS = 2048

    VER_PERITOS = 4096
    MODIFICAR_PERITOS = 8192
    CREAR_PERITOS = 16384

    VER_LISTAS_DE_ACUERDOS = 32768
    MODIFICAR_LISTAS_DE_ACUERDOS = 65536
    CREAR_LISTAS_DE_ACUERDOS = 131072

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
                Permiso.VER_CONTENIDOS,
                Permiso.MODIFICAR_CONTENIDOS,
                Permiso.CREAR_CONTENIDOS,
            ],
            "SOPORTE TECNICO": [
                Permiso.VER_CUENTAS,
                Permiso.MODIFICAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONTENIDOS,
            ],
            "JUZGADO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONTENIDOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.MODIFICAR_LISTAS_DE_ACUERDOS,
                Permiso.CREAR_LISTAS_DE_ACUERDOS,
            ],
            "SECRETARIA TECNICA": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONTENIDOS,
                Permiso.VER_ABOGADOS,
                Permiso.MODIFICAR_ABOGADOS,
                Permiso.CREAR_ABOGADOS,
                Permiso.VER_PERITOS,
                Permiso.MODIFICAR_PERITOS,
                Permiso.CREAR_PERITOS,
            ],
            "USUARIO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONTENIDOS,
            ],
            "OBSERVADOR": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONTENIDOS,
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
        if module == "usuarios":
            return True
        if module in ("bitacoras", "entradas_salidas", "roles", "tareas"):
            return self.has_permission(Permiso.VER_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.VER_CATALOGOS)
        if module in ("abogados", "edictos", "glosas", "listas_de_acuerdos", "peritos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.VER_CONTENIDOS)
        return False

    def can_insert(self, module):
        """ ¿Tiene permiso para agregar? """
        if module in ("usuarios", "bitacoras", "entradas_salidas", "roles", "tareas"):
            return self.has_permission(Permiso.MODIFICAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.MODIFICAR_CATALOGOS)
        if module in ("abogados", "edictos", "glosas", "listas_de_acuerdos", "peritos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.MODIFICAR_CONTENIDOS)
        return False

    def can_edit(self, module):
        """ ¿Tiene permiso para editar? """
        if module in ("usuarios", "bitacoras", "entradas_salidas", "roles", "tareas"):
            return self.has_permission(Permiso.CREAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.CREAR_CATALOGOS)
        if module in ("abogados", "edictos", "glosas", "listas_de_acuerdos", "peritos", "sentencias", "tareas", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.CREAR_CONTENIDOS)
        return False

    def __repr__(self):
        """ Representación """
        return f"<Rol {self.nombre}>"
