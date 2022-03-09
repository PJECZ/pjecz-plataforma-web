"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, RadioField, DateField, IntegerField
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

    usuario = StringField("Usted es")  # Read only
    oficina = StringField("Se encuentra en")  # Read only
    descripcion = TextAreaField("1. Escriba detalladamente el problema", validators=[DataRequired(), Length(max=4000)])
    clasificacion = RadioField("2. Elija una clasificación", choices=SoporteTicket.CLASIFICACIONES, default="OTRO", validators=[DataRequired()])
    guardar = SubmitField("Solicitar soporte al personal de Informática")


class SoporteTicketNewForUsuarioForm(FlaskForm):
    """Formulario para que un administrador pueda crear un ticket para otro usuario"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema", validators=[DataRequired(), Length(max=4000)])
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    guardar = SubmitField("Guardar como abierto")


class SoporteTicketEditForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema", validators=[DataRequired(), Length(max=4000)])
    categoria = StringField(label="Categoría")  # Read only
    tecnico = StringField(label="Técnico")  # Read only
    estado = StringField("Estado")  # Read only
    guardar = SubmitField("Guardar")


class SoporteTicketTakeForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    tecnico = StringField("Técnico")  # Read only
    guardar = SubmitField("Tomar")


class SoporteTicketCategorizeForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = QuerySelectField(label="Categoría", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    guardar = SubmitField("Categorizar")


class SoporteTicketCloseForm(FlaskForm):
    """Formulario SoporteTicket"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = StringField("Categoría")  # Read only
    tecnico = StringField("Técnico")  # Read only
    soluciones = TextAreaField("Motivo", validators=[DataRequired(), Length(max=1024)])
    guardar = SubmitField("Cerrar")


class SoporteTicketDoneForm(FlaskForm):
    """Formulario SoporteTicket TERMINAR"""

    usuario = StringField("Usuario")  # Read only
    descripcion = TextAreaField("Descripción del problema")  # Read only
    categoria = StringField("Categoría")  # Read only
    tecnico = StringField("Técnico")  # Read only
    soluciones = TextAreaField("Solución", validators=[DataRequired(), Length(max=1024)])
    guardar = SubmitField("Terminar")


class SoporteTicketSearchForm(FlaskForm):
    """Formulario de búsqueda de Ticekts"""

    id = IntegerField("ID", validators=[Optional()])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=256)])
    solucion = StringField("Solución", validators=[Optional(), Length(max=256)])
    estado = SelectField("Estado", choices=SoporteTicket.ESTADOS, validators=[Optional()])
    creado_desde = DateField("Creados desde", validators=[Optional()])
    creado_hasta = DateField("Creados hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")
