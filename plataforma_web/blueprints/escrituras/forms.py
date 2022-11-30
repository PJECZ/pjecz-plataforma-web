"""
Escrituras, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP
from plataforma_web.blueprints.escrituras.models import Escritura

from lib.wtforms import JSONField


class EscrituraForm(FlaskForm):
    """Formulario para Escritura que usan las notarias"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Notaría")  # Read only
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    tipo = SelectField("Tipo de procedimiento", choices=Escritura.TIPOS, validators=[DataRequired()])
    texto = JSONField("Texto", validators=[Optional()])
    # texto = TextAreaField("Texto", validators=[DataRequired()], render_kw={"rows": 12})
    guardar = SubmitField("Guardar")


class EscrituraReviewForm(FlaskForm):
    """Formulario para editar Escritura que usan los administradores"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Notaría")  # Read only
    aprobacion_fecha = DateField("Fecha de aprobación", validators=[DataRequired()])
    etapa = SelectField("Etapa del procedimiento", choices=Escritura.ETAPAS, validators=[DataRequired()])
    expediente = StringField("Expediente")  # Read only
    observaciones = TextAreaField("Observaciones", validators=[Optional()], render_kw={"rows": 4})
    tipo = SelectField("Tipo de procedimiento", choices=Escritura.TIPOS, validators=[DataRequired()])
    texto = TextAreaField("Texto", render_kw={"rows": 12})  # Read only
    guardar = SubmitField("Guardar")
