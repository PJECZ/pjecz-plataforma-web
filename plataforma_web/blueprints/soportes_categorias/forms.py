"""
Soportes Categorias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.roles.models import Rol


def roles_opciones():
    """Rol: opciones para select"""
    return Rol.query.filter_by(estatus="A").order_by(Rol.nombre).all()


class SoporteCategoriaForm(FlaskForm):
    """Formulario SoporteCategoria"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    rol = QuerySelectField("Rol", query_factory=roles_opciones, get_label="nombre", validators=[Optional()])
    instrucciones = TextAreaField("Instrucciones", validators=[Optional(), Length(max=4096)])
    guardar = SubmitField("Guardar")
