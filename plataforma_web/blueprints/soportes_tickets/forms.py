"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class SoporteTicketNewForm(FlaskForm):
    """Formulario SoporteTicket"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class SoporteTicketTakeForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class SoporteTicketCloseForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # soluciones
    guardar = SubmitField("Guardar")
