"""
Usuarios-Roles, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.roles.models import Rol


def roles_opciones():
    """Roles: opciones para select"""
    return Rol.query.filter_by(estatus="A").order_by(Rol.nombre).all()


class UsuarioRolWithUsuarioForm(FlaskForm):
    """Formulario UsuarioRol"""

    rol = QuerySelectField(query_factory=roles_opciones, get_label="nombre", validators=[DataRequired()])
    usuario = StringField("Usuario")  # Solo lectura
    guardar = SubmitField("Guardar")
