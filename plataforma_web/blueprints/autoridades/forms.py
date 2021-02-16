"""
Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito


def distritos_opciones():
    """ Distritos: opciones para select """
    return Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()


class AutoridadNewForm(FlaskForm):
    """ Formulario nueva Autoridad """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Autoridad", validators=[DataRequired(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Email()])
    # directorio_listas_de_acuerdos
    # directorio_sentencias
    guardar = SubmitField("Guardar")


class AutoridadEditForm(FlaskForm):
    """ Formulario modificar Autoridad """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Autoridad", validators=[DataRequired(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Email()])
    directorio_listas_de_acuerdos = StringField("Directorio listas de acuerdos", validators=[Optional(), Length(max=256)])
    directorio_sentencias = StringField("Directorio listas de acuerdos", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
