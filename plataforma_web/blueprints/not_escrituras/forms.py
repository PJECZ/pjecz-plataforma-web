"""
Not Escrituras, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from lib.wtforms import JSONField

from plataforma_web.blueprints.not_escrituras.models import NotEscritura


class NotEscriturasForm(FlaskForm):
    """Formulario NotEscrituras"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    juzgado = SelectField("Juzgado", coerce=int, validate_choice=False, validators=[Optional()])
    estado = SelectField("Estado", choices=NotEscritura.ESTADOS, validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    guardar = SubmitField("Guardar")


class NotEscriturasEditForm(FlaskForm):
    """Formulario NotEscrituras"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    juzgado = StringField("Juzgado")
    estado = SelectField("Estado", choices=NotEscritura.ESTADOS, validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    guardar = SubmitField("Guardar")
