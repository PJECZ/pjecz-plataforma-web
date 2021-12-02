"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from .models import SoporteTicket
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria

def tecnicos_opciones():
    """Seleccionar Funcionario: opciones para select"""
    return Funcionario.query.filter_by(estatus="A").order_by(Funcionario.nombres).filter(Funcionario.en_soportes==True).all()

def categorias_opciones():
    """Seleccionar la categoría para select"""
    return SoporteCategoria.query.filter_by(estatus="A").order_by(SoporteCategoria.nombre).all()


class SoporteTicketNewForm(FlaskForm):
    """Formulario SoporteTicket"""

    descripcion = TextAreaField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Envíar")


class SoporteTicketEditForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[Optional()])
    tecnico = QuerySelectField(label="Técnico", query_factory=tecnicos_opciones, get_label="nombre", validators=[Optional()])
    estado = SelectField("Estado", choices=SoporteTicket.ESTADOS)
    soluciones = TextAreaField("Solución", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class SoporteTicketTakeForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[Optional()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Tomar")


class SoporteTicketCloseForm(FlaskForm):
    """Formulario SoporteTicket"""

    # soporte_categoria
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # soluciones
    guardar = SubmitField("Resuelto")
