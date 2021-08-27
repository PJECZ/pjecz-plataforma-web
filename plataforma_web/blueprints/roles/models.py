"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Permiso:
    """Permiso tiene como constantes enteros de potencia dos"""

    # CUENTAS: Usuarios, Bitácoras, Entradas-Salidas, Roles, Tareas, Transcripciones
    VER_CUENTAS = 0b1
    MODIFICAR_CUENTAS = 0b10
    CREAR_CUENTAS = MODIFICAR_CUENTAS

    # CATALOGOS: Distritos, Autoridades
    VER_CATALOGOS = 0b100
    MODIFICAR_CATALOGOS = 0b1000
    CREAR_CATALOGOS = MODIFICAR_CATALOGOS

    # DOCUMENTACIONES
    VER_DOCUMENTACIONES = 0b10000
    MODIFICAR_DOCUMENTACIONES = 0b100000
    CREAR_DOCUMENTACIONES = MODIFICAR_DOCUMENTACIONES

    # CONSULTAS: Abogados, Peritos
    VER_CONSULTAS = 0b1000000
    MODIFICAR_CONSULTAS = 0b10000000
    CREAR_CONSULTAS = MODIFICAR_CONSULTAS

    # JUSTICIABLES: Listas de Acuerdos, Sentencias, Ubicación de expedientes
    VER_JUSTICIABLES = 0b100000000
    MODIFICAR_JUSTICIABLES = 0b1000000000
    CREAR_JUSTICIABLES = MODIFICAR_JUSTICIABLES
    ADMINISTRAR_JUSTICIABLES = 0b10000000000

    # NOTARIALES: Edictos
    VER_NOTARIALES = 0b100000000000
    MODIFICAR_NOTARIALES = 0b1000000000000
    CREAR_NOTARIALES = MODIFICAR_NOTARIALES
    ADMINISTRAR_NOTARIALES = 0b10000000000000

    # PLENOS SALAS TRIBUNALES TCA: Glosas
    VER_SEGUNDAS = 0b100000000000000
    MODIFICAR_SEGUNDAS = 0b1000000000000000
    CREAR_SEGUNDAS = MODIFICAR_SEGUNDAS
    ADMINISTRAR_SEGUNDAS = 0b10000000000000000

    def __repr__(self):
        """Representación"""
        return "<Permiso>"


class Rol(db.Model, UniversalMixin):
    """Rol"""

    # Nombre de la tabla
    __tablename__ = "roles"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    permiso = db.Column(db.Integer, nullable=False)
    por_defecto = db.Column(db.Boolean, default=False, index=True)

    # Hijos
    usuarios = db.relationship("Usuario", back_populates="rol")

    def add_permission(self, perm):
        """Agregar permiso"""
        if not self.has_permission(perm):
            self.permiso += perm

    def remove_permission(self, perm):
        """Retirar permiso"""
        if self.has_permission(perm):
            self.permiso -= perm

    def reset_permissions(self):
        """Poner permisos a cero"""
        self.permiso = 0

    def has_permission(self, perm):
        """¿Tiene el permiso dado?"""
        return self.permiso & perm == perm

    @staticmethod
    def insert_roles():
        """Insertar roles iniciales"""
        roles = {
            "ADMINISTRADOR": [
                Permiso.VER_CUENTAS,
                Permiso.MODIFICAR_CUENTAS,
                Permiso.CREAR_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.MODIFICAR_CATALOGOS,
                Permiso.CREAR_CATALOGOS,
                Permiso.VER_DOCUMENTACIONES,
                Permiso.MODIFICAR_DOCUMENTACIONES,
                Permiso.CREAR_DOCUMENTACIONES,
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
                Permiso.VER_SEGUNDAS,
                Permiso.MODIFICAR_SEGUNDAS,
                Permiso.CREAR_SEGUNDAS,
                Permiso.ADMINISTRAR_SEGUNDAS,
            ],
            "SOPORTE TECNICO": [
                Permiso.VER_CUENTAS,
                Permiso.VER_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "JUZGADO": [
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.MODIFICAR_JUSTICIABLES,
                Permiso.CREAR_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.MODIFICAR_NOTARIALES,
                Permiso.CREAR_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "NOTARIA": [
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.MODIFICAR_NOTARIALES,
                Permiso.CREAR_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "SECRETARIA TECNICA": [
                Permiso.VER_CATALOGOS,
                Permiso.MODIFICAR_CATALOGOS,
                Permiso.CREAR_CATALOGOS,
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "USUARIO": [
                Permiso.VER_CATALOGOS,
                Permiso.VER_DOCUMENTACIONES,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "OBSERVADOR": [
                Permiso.VER_CATALOGOS,
                Permiso.VER_DOCUMENTACIONES,
                Permiso.VER_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.VER_SEGUNDAS,
            ],
            "PLENOS SALAS TRIBUNALES TCA": [
                Permiso.VER_CONSULTAS,
                Permiso.MODIFICAR_CONSULTAS,
                Permiso.CREAR_CONSULTAS,
                Permiso.VER_JUSTICIABLES,
                Permiso.MODIFICAR_JUSTICIABLES,
                Permiso.CREAR_JUSTICIABLES,
                Permiso.VER_NOTARIALES,
                Permiso.MODIFICAR_NOTARIALES,
                Permiso.CREAR_NOTARIALES,
                Permiso.VER_SEGUNDAS,
                Permiso.MODIFICAR_SEGUNDAS,
                Permiso.CREAR_SEGUNDAS,
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
        return len(roles)

    def can_view(self, module):
        """¿Tiene permiso para ver?"""
        if module in ("bitacoras", "entradas_salidas", "modulos", "rep_graficas", "rep_reportes", "rep_resultados", "roles", "tareas", "usuarios"):
            return self.has_permission(Permiso.VER_CUENTAS)
        if module in ("distritos", "autoridades", "materias", "materias_tipos_juicios"):
            return self.has_permission(Permiso.VER_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros"):
            return self.has_permission(Permiso.VER_DOCUMENTACIONES)
        if module in ("abogados", "peritos"):
            return self.has_permission(Permiso.VER_CONSULTAS)
        if module in ("audiencias", "listas_de_acuerdos", "listas_de_acuerdos_acuerdos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.VER_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.VER_NOTARIALES)
        if module == "glosas":
            return self.has_permission(Permiso.VER_SEGUNDAS)
        return False

    def can_insert(self, module):
        """¿Tiene permiso para agregar?"""
        if module in ("bitacoras", "entradas_salidas", "modulos", "rep_graficas", "rep_reportes", "rep_resultados", "roles", "tareas", "usuarios"):
            return self.has_permission(Permiso.MODIFICAR_CUENTAS)
        if module in ("distritos", "autoridades", "materias", "materias_tipos_juicios"):
            return self.has_permission(Permiso.MODIFICAR_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros"):
            return self.has_permission(Permiso.MODIFICAR_DOCUMENTACIONES)
        if module in ("abogados", "peritos"):
            return self.has_permission(Permiso.MODIFICAR_CONSULTAS)
        if module in ("audiencias", "listas_de_acuerdos", "listas_de_acuerdos_acuerdos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.MODIFICAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.MODIFICAR_NOTARIALES)
        if module == "glosas":
            return self.has_permission(Permiso.MODIFICAR_SEGUNDAS)
        return False

    def can_edit(self, module):
        """¿Tiene permiso para editar?"""
        if module in ("bitacoras", "entradas_salidas", "modulos", "rep_graficas", "rep_reportes", "rep_resultados", "roles", "tareas", "usuarios"):
            return self.has_permission(Permiso.CREAR_CUENTAS)
        if module in ("distritos", "autoridades", "materias", "materias_tipos_juicios"):
            return self.has_permission(Permiso.CREAR_CATALOGOS)
        if module in ("cid_procedimientos", "cid_formatos", "cid_registros"):
            return self.has_permission(Permiso.CREAR_DOCUMENTACIONES)
        if module in ("abogados", "peritos"):
            return self.has_permission(Permiso.CREAR_CONSULTAS)
        if module in ("audiencias", "listas_de_acuerdos", "listas_de_acuerdos_acuerdos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.CREAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.CREAR_NOTARIALES)
        if module == "glosas":
            return self.has_permission(Permiso.CREAR_SEGUNDAS)
        return False

    def can_admin(self, module):
        """¿Tiene permiso para administrar?"""
        if module in ("audiencias", "listas_de_acuerdos", "listas_de_acuerdos_acuerdos", "sentencias", "ubicaciones_expedientes"):
            return self.has_permission(Permiso.ADMINISTRAR_JUSTICIABLES)
        if module == "edictos":
            return self.has_permission(Permiso.ADMINISTRAR_NOTARIALES)
        if module == "glosas":
            return self.has_permission(Permiso.ADMINISTRAR_SEGUNDAS)
        return False

    def __repr__(self):
        """Representación"""
        return f"<Rol {self.nombre}>"
