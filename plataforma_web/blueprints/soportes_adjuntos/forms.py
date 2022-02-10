"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
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


class SoporteAdjuntoNewForm(FlaskForm):
    """Formulario para subir archivos"""

    usuario = StringField("Usuario")  # Read only
    problema = TextAreaField("Descripción del problema")  # Read only
    categoria = StringField("Categoría")  # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
