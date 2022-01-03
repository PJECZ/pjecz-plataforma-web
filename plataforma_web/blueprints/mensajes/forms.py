"""
Mensaje, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.usuarios.models import Usuario


def usuarios_opciones():
    """Usuarios: opciones para select"""
    return Usuario.query.filter_by(estatus="A").order_by(Usuario.email).all()


class MensajeForm(FlaskForm):
    """Formulario Mensaje"""

    destinatario = QuerySelectField("Destinatario", query_factory=usuarios_opciones, get_label="email", validators=[DataRequired()])
    asunto = StringField("Asunto", validators=[DataRequired(), Length(max=128)])
    contenido = TextAreaField("Contenido", validators=[DataRequired(), Length(max=512)])
    enviar = SubmitField("Enviar")


class MensajeRespuestaForm(FlaskForm):
    """Respueta a un Mensaje"""

    asunto = StringField("Asunto", validators=[DataRequired(), Length(max=128)])
    respuesta = TextAreaField("Respuesta", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Envíar")
