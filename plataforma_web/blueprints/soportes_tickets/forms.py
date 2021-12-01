"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class SoporteTicketNewForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    # funcionario
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # estado
    # resolucion
    # soluciones
    guardar = SubmitField("Guardar")


class SoporteTicketTakeForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    # funcionario
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # estado
    # resolucion
    # soluciones
    guardar = SubmitField("Guardar")


class SoporteTicketCloseForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    # funcionario
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # estado
    # resolucion
    # soluciones
    guardar = SubmitField("Guardar")
