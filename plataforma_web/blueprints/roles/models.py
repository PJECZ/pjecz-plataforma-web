"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Permiso:
    """ Permiso tiene como constantes enteros de potencia dos """

    VER_CUENTAS = 0b1
    MODIFICAR_CUENTAS = 0b10
    CREAR_CUENTAS = 0b100

    VER_CATALOGOS = 0b1000
    MODIFICAR_CATALOGOS = 0b10000
    CREAR_CATALOGOS = 0b100000

    VER_TAREAS = 0b1000000
    MODIFICAR_TAREAS = 0b10000000
    CREAR_TAREAS = 0b100000000

    VER_CONSULTAS = 0b1000000000
    MODIFICAR_CONSULTAS = 0b10000000000
    CREAR_CONSULTAS = 0b100000000000

    VER_EDICTOS = 0b1000000000000
    MODIFICAR_EDICTOS = 0b10000000000000
    CREAR_EDICTOS = 0b10000000000000

    VER_LISTAS_DE_ACUERDOS = 0b100000000000000
    MODIFICAR_LISTAS_DE_ACUERDOS = 0b1000000000000000
    CREAR_LISTAS_DE_ACUERDOS = 0b10000000000000000

    VER_SENTENCIAS = 0b100000000000000000
    MODIFICAR_SENTENCIAS = 0b1000000000000000000
    CREAR_SENTENCIAS = 0b10000000000000000000

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
                Permiso.VER_TAREAS,
                Permiso.MODIFICAR_TAREAS,
                Permiso.CREAR_TAREAS,
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_EDICTOS,
                Permiso.MODIFICAR_EDICTOS,
                Permiso.CREAR_EDICTOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.MODIFICAR_LISTAS_DE_ACUERDOS,
                Permiso.CREAR_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
                Permiso.MODIFICAR_SENTENCIAS,
                Permiso.CREAR_SENTENCIAS,
            ],
            "SOPORTE TECNICO": [
                Permiso.VER_CUENTAS,
                Permiso.MODIFICAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_TAREAS,
                Permiso.MODIFICAR_TAREAS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_EDICTOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
            ],
            "JUZGADO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_TAREAS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.MODIFICAR_LISTAS_DE_ACUERDOS,
                Permiso.CREAR_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
                Permiso.MODIFICAR_SENTENCIAS,
                Permiso.CREAR_SENTENCIAS,
            ],
            "SECRETARIA TECNICA": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_TAREAS,
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_EDICTOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
            ],
            "USUARIO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_TAREAS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_EDICTOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
            ],
            "OBSERVADOR": [
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_EDICTOS,
                Permiso.VER_LISTAS_DE_ACUERDOS,
                Permiso.VER_SENTENCIAS,
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
        if module in ("bitacoras", "entradas_salidas", "roles"):
            return self.has_permission(Permiso.VER_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.VER_CATALOGOS)
        if module in ("tareas", "transcripciones"):
            return self.has_permission(Permiso.VER_TAREAS)
        if module in ("abogados", "glosas", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.VER_CONSULTAS)
        if module == "edictos":
            return self.has_permission(Permiso.VER_EDICTOS)
        if module == "listas_de_acuerdos":
            return self.has_permission(Permiso.VER_LISTAS_DE_ACUERDOS)
        if module == "sentencias":
            return self.has_permission(Permiso.VER_SENTENCIAS)
        return False

    def can_insert(self, module):
        """ ¿Tiene permiso para agregar? """
        if module == "usuarios":
            return self.has_permission(Permiso.MODIFICAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.MODIFICAR_CATALOGOS)
        if module in ("tareas", "transcripciones"):
            return self.has_permission(Permiso.MODIFICAR_TAREAS)
        if module in ("abogados", "glosas", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.MODIFICAR_CONSULTAS)
        if module == "edictos":
            return self.has_permission(Permiso.MODIFICAR_EDICTOS)
        if module == "listas_de_acuerdos":
            return self.has_permission(Permiso.MODIFICAR_LISTAS_DE_ACUERDOS)
        if module == "sentencias":
            return self.has_permission(Permiso.MODIFICAR_SENTENCIAS)
        return False

    def can_edit(self, module):
        """ ¿Tiene permiso para editar? """
        if module == "usuarios":
            return self.has_permission(Permiso.CREAR_CUENTAS)
        if module in ("distritos", "autoridades"):
            return self.has_permission(Permiso.CREAR_CATALOGOS)
        if module in ("tareas", "transcripciones"):
            return self.has_permission(Permiso.CREAR_TAREAS)
        if module in ("abogados", "glosas", "peritos", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.CREAR_CONSULTAS)
        if module == "edictos":
            return self.has_permission(Permiso.CREAR_EDICTOS)
        if module == "listas_de_acuerdos":
            return self.has_permission(Permiso.CREAR_LISTAS_DE_ACUERDOS)
        if module == "sentencias":
            return self.has_permission(Permiso.CREAR_SENTENCIAS)
        return False

    def __repr__(self):
        """ Representación """
        return f"<Rol {self.nombre}>"
