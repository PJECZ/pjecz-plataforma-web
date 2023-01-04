"""
Not Escrituras, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from lib.wtforms import JSONField
from lib.safe_string import EXPEDIENTE_REGEXP

from plataforma_web.blueprints.not_escrituras.models import NotEscritura


class NotEscriturasForm(FlaskForm):
    """Formulario NotEscrituras"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    juzgado = SelectField(label="Juzgado", coerce=int, validators=[Optional()], validate_choice=False)
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    estado = HiddenField("Estado", validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    guardar = SubmitField("Guardar Borrador")
    enviar = SubmitField("Enviar")


class NotEscriturasEditForm(FlaskForm):
    """Formulario NotEscrituras"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    juzgado = SelectField(label="Juzgado", coerce=int, validators=[Optional()], validate_choice=False)
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    estado = HiddenField("Estado", validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    guardar = SubmitField("Guardar Borrador")
    revision = SubmitField("Revisar")
    enviar = SubmitField("Enviar")


class NotEscriturasEditJuzgadoForm(FlaskForm):
    """Formulario NotEscrituras"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    juzgado = StringField("Juzgado")  # Read only
    # juzgado = SelectField(label="Juzgado", coerce=int, validators=[Optional()], validate_choice=False)
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    estado = HiddenField("Estado", validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    revision = SubmitField("Revisar")
    finalizado = SubmitField("Finalizado")
