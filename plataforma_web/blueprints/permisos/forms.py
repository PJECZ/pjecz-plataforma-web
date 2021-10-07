"""
Permisos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired

from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.roles.models import Rol

NIVELES = [
    (1, "VER"),
    (2, "VER y MODIFICAR"),
    (3, "VER, MODIFICAR y CREAR"),
    (4, "ADMINISTRAR"),
]


def modulos_opciones():
    """Modulos: opciones para select"""
    return Modulo.query.filter_by(estatus="A").order_by(Modulo.nombre).all()


def roles_opciones():
    """Roles: opciones para select"""
    return Rol.query.filter_by(estatus="A").order_by(Rol.nombre).all()


class PermisoNewForm(FlaskForm):
    """Formulario Permiso"""

    modulo = QuerySelectField(query_factory=modulos_opciones, get_label="nombre", validators=[DataRequired()])
    rol = QuerySelectField(query_factory=roles_opciones, get_label="nombre", validators=[DataRequired()])
    nivel = SelectField("Nivel", validators=[DataRequired()], choices=NIVELES, coerce=int)
    guardar = SubmitField("Guardar")


class PermisoNewWithModuloForm(FlaskForm):
    """Formulario Permiso"""

    modulo = StringField("Módulo")  # Solo lectura
    rol = QuerySelectField(query_factory=roles_opciones, get_label="nombre", validators=[DataRequired()])
    nivel = SelectField("Nivel", validators=[DataRequired()], choices=NIVELES, coerce=int)
    guardar = SubmitField("Guardar")


class PermisoNewWithRolForm(FlaskForm):
    """Formulario Permiso"""

    modulo = QuerySelectField(query_factory=modulos_opciones, get_label="nombre", validators=[DataRequired()])
    rol = StringField("Rol")  # Solo lectura
    nivel = SelectField("Nivel", validators=[DataRequired()], choices=NIVELES, coerce=int)
    guardar = SubmitField("Guardar")


class PermisoEditForm(FlaskForm):
    """Formulario Permiso"""

    nivel = SelectField("Nivel", validators=[DataRequired()], choices=NIVELES, coerce=int)
    guardar = SubmitField("Guardar")
