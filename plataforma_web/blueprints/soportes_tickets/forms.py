"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket


def tecnicos_opciones():
    """Seleccionar Funcionario: opciones para select"""
    return Funcionario.query.filter_by(estatus="A").order_by(Funcionario.nombres).filter_by(en_soportes=True).all()

def categorias_opciones():
    """Seleccionar la categoría para select"""
    return SoporteCategoria.query.filter_by(estatus="A").order_by(SoporteCategoria.nombre).all()


class SoporteTicketNewForm(FlaskForm):
    """Formulario para que cualquier usuario pueda crear un ticket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema", validators=[DataRequired(), Length(max=1024)])
    guardar = SubmitField("Solicitar soporte al personal de Informática")


class SoporteTicketNewForUsuarioForm(FlaskForm):
    """Formulario para que un administrador pueda crear un ticket para otro usuario"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema", validators=[DataRequired(), Length(max=1024)])
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    guardar = SubmitField("Solicitar soporte al personal de Informática")


class SoporteTicketEditForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    tecnico = QuerySelectField(label="Técnico", query_factory=tecnicos_opciones, get_label="nombre", validators=[DataRequired()], allow_blank=True)
    soluciones = TextAreaField("Solución", validators=[Optional(), Length(max=1024)])
    estado = SelectField("Estado", choices=SoporteTicket.ESTADOS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class SoporteTicketTakeForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    tecnico = StringField("Técnico")  # Read only
    guardar = SubmitField("Tomar")


class SoporteTicketCloseForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = StringField("Categoría")  # Read only
    tecnico = StringField("Técnico")  # Read only
    soluciones = TextAreaField("Solución", validators=[DataRequired(), Length(max=1024)])
    guardar = SubmitField("Resuelto")
