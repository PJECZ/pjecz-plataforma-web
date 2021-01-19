"""
Peritos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Perito(db.Model, UniversalMixin):
    """ Perito """

    TIPOS = OrderedDict([
        ('ALBACEA', 'Albacea'),
        ('AMBIENTAL', 'Ambiental'),
        ('ARBITRO VOLUNTARIO', 'Árbitro Voluntario'),
        ('AUDITORIA INTERNA', 'Auditoría Interna'),
        ('BALISTICA', 'Balística'),
        ('CONTABILIDAD', 'Contabilidad'),
        ('CRIMINOLOGIA', 'Criminología'),
        ('CRIMINALISTICA', 'Criminalística'),
        ('DACTILOSCOPIA', 'Dactiloscopía'),
        ('DEPOSITARIO', 'Depositario'),
        ('DOCUMENTOSCOPIA', 'Documentoscopía'),
        ('FOTOGRAFIA FORENSE', 'Fotografía Forence'),
        ('GASTROENTEROLOGIA', 'Gastroenterología'),
        ('GENETICA', 'Genética'),
        ('GRAFOSCOPIA', 'Grafoscopía'),
        ('HECHOS DE TRANSITO TERRESTRE', 'Hechos de Tránsito Terrestre'),
        ('INCENDIOS Y EXPLOSIVOS', 'Incendios y Explosivos'),
        ('INTERPRETE EN LENGUA DE SEÑAS MEXICANAS', 'Intérprete en Lengua de Señas Mexicanas'),
        ('INTERVENTORES', 'Interventores'),
        ('MEDICINA', 'Medicina'),
        ('MEDICINA FORENCE', 'Medicina Forence'),
        ('ODONTOLOGIA LEGAL Y FORENCE', 'Odontología Legal y Forense'),
        ('PSICOLOGIA', 'Psicología'),
        ('TOPOGRAFIA', 'Topografía'),
        ('TRADUCCION', 'Traducción'),
        ('TRANSITO Y VIALIDAD TERRESTRE', 'Tránsito y Vialidad Terrestre'),
        ('TUTORES', 'Tutores'),
        ('VALUACION', 'Valuación'),
        ('VALUACION VEHICULOS DAÑADOS', 'Valuación Vehículos Dañados'),
    ])

    # Nombre de la tabla
    __tablename__ = 'peritos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column(
        'distrito',
        db.Integer,
        db.ForeignKey('distritos.id'),
        index=True,
        nullable=False
    )

    # Columnas
    tipo = db.Column(
        db.Enum(*TIPOS, name='tipos_peritos', native_enum=False),
        index=True,
        nullable=False,
    )
    nombre = db.Column(db.String(256), nullable=False)
    domicilio = db.Column(db.String(256), nullable=False)
    telefono_fijo = db.Column(db.String(64))
    telefono_celular = db.Column(db.String(64))
    email = db.Column(db.String(256))
    notas = db.Column(db.String(256))

    def __repr__(self):
        """ Representación """
        return f'<Perito {self.nombre}>'
