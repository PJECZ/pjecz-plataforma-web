"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Permiso:
    """ Permiso tiene como constantes enteros de potencia dos """

    VER_CATALOGOS = 1
    MODIFICAR_CATALOGOS = 2
    CREAR_CATALOGOS = 4
    VER_ESTADISTICAS = 8
    MODIFICAR_ESTADISTICAS = 16
    CREAR_ESTADISTICAS = 32
    VER_CUENTAS = 64
    MODIFICAR_CUENTAS = 128
    CREAR_CUENTAS = 256

    def __repr__(self):
        """ Representación """
        return '<Permiso>'


class Rol(db.Model, UniversalMixin):
    """ Rol """

    # Nombre de la tabla
    __tablename__ = 'roles'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    permiso = db.Column(db.Integer, nullable=False)
    por_defecto = db.Column(db.Boolean, default=False, index=True)

    # Hijos
    usuarios = db.relationship('Usuario', backref='rol')

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
            'ADMINISTRADOR': [
                Permiso.VER_CUENTAS, Permiso.MODIFICAR_CUENTAS, Permiso.CREAR_CUENTAS,
                Permiso.VER_CATALOGOS, Permiso.MODIFICAR_CATALOGOS, Permiso.CREAR_CATALOGOS,
                Permiso.VER_ESTADISTICAS, Permiso.MODIFICAR_ESTADISTICAS, Permiso.CREAR_ESTADISTICAS,
            ],
            'TECNICO': [
                Permiso.VER_CUENTAS, Permiso.MODIFICAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_ESTADISTICAS,
            ],
            'USUARIO': [
                Permiso.VER_CATALOGOS,
                Permiso.VER_ESTADISTICAS, Permiso.MODIFICAR_ESTADISTICAS, Permiso.CREAR_ESTADISTICAS,
            ],
            'OBSERVADOR': [
                Permiso.VER_CATALOGOS,
                Permiso.VER_ESTADISTICAS,
            ],
        }
        rol_por_defecto = 'OBSERVADOR'
        for item in roles:
            rol = Rol.query.filter_by(nombre=item).first()
            if rol is None:
                rol = Rol(nombre=item)
            rol.reset_permissions()
            for perm in roles[item]:
                rol.add_permission(perm)
            rol.por_defecto = (rol.nombre == rol_por_defecto)
            db.session.add(rol)
        db.session.commit()

    def can_view(self, module):
        """ ¿Tiene permiso para ver? """
        if module == 'usuarios':
            return True
        if module in ('bitacoras', 'entradas_salidas', 'roles'):
            return self.has_permission(Permiso.VER_CUENTAS)
        if module in ('distritos', 'autoridades'):
            return self.has_permission(Permiso.VER_CATALOGOS)
        # if module in ():
        #     return self.has_permission(Permiso.VER_ESTADISTICAS)
        return False

    def can_insert(self, module):
        """ ¿Tiene permiso para agregar? """
        if module in ('usuarios'):
            return self.has_permission(Permiso.MODIFICAR_CUENTAS)
        if module in ('distritos', 'autoridades'):
            return self.has_permission(Permiso.MODIFICAR_CATALOGOS)
        # if module in ():
        #     return self.has_permission(Permiso.MODIFICAR_ESTADISTICAS)
        return False

    def can_edit(self, module):
        """ ¿Tiene permiso para editar? """
        if module in ('usuarios'):
            return self.has_permission(Permiso.CREAR_CUENTAS)
        if module in ('distritos', 'autoridades'):
            return self.has_permission(Permiso.CREAR_CATALOGOS)
        # if module in ():
        #     return self.has_permission(Permiso.CREAR_ESTADISTICAS)
        return False

    def __repr__(self):
        """ Representación """
        return f'<Rol {self.nombre}>'
