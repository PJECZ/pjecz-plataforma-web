"""
Peritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField,  SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.peritos.models import Perito


def distritos_opciones():
    """ Distritos: opciones para select """
    return Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()


class PeritoForm(FlaskForm):
    """ Formulario Perito """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    tipo = SelectField("Tipo", choices=Perito.TIPOS)
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    domicilio = StringField("Domicilio", validators=[DataRequired(), Length(max=256)])
    telefono_fijo = StringField("Teléfono fijo", validators=[Optional(), Length(max=256)])
    telefono_celular = StringField("Teléfono celular", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Email()])
    renovacion = DateField("Renovación", validators=[DataRequired()])
    notas = StringField("Notas", validators=[Optional()])
    guardar = SubmitField("Guardar")


class PeritoSearchForm(FlaskForm):
    """ Formulario para buscar Peritos """

    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    tipo = SelectField("Tipo", choices=Perito.TIPOS, validators=[Optional()])
    buscar = SubmitField("Buscar")
