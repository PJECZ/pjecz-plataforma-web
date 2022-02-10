"""
Soportes Adjuntos, vistas
"""
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib import datatables
from lib.safe_string import safe_string, safe_message
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.soportes_adjuntos.models import SoporteAdjunto
from plataforma_web.blueprints.soportes_tickets.models import SoporteTicket
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.soportes_adjuntos.forms import SoporteAdjuntoNewForm

MODULO = "SOPORTES ADJUNTOS"
SUBDIRECTORIO = "cit_archivos"

soportes_adjuntos = Blueprint("soportes_adjuntos", __name__, template_folder="templates")


def _get_funcionario_from_current_user():
    """Consultar el funcionario (si es de soporte) a partir del usuario actual"""
    funcionario = Funcionario.query.filter(Funcionario.email == current_user.email).first()
    if funcionario is None:
        return None  # No existe el funcionario
    if funcionario.estatus != "A":
        return None  # No es activo
    if funcionario.en_soportes is False:
        return None  # No es de soporte
    return funcionario


@soportes_adjuntos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""



@soportes_adjuntos.route("/soportes_adjuntos/<int:soporte_adjunto_id>")
def detail(soporte_adjunto_id):
    """Detalle de un Soporte Ticket"""
    soporte_adjunto = SoporteAdjunto.query.get_or_404(soporte_adjunto_id)
    return render_template(
        "soportes_adjuntos/detail.jinja2",
        soporte_adjunto=soporte_adjunto,
        funcionario=_get_funcionario_from_current_user(),
    )


@soportes_adjuntos.route("/soportes_adjuntos/nuevo/<int:soporte_ticket_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(soporte_ticket_id):
    """Adjuntar Archivos al Ticket"""
    ticket = SoporteTicket.query.get_or_404(soporte_ticket_id)
    #archivo = SoporteTicketFile
    detalle_url = url_for("soportes_tickets.detail", soporte_ticket_id=ticket.id)
    if ticket.estatus != "A":
        flash("No puede adjuntar un archivo a un ticket eliminado.", "warning")
        return redirect(detalle_url)
    if ticket.estado is ("ABIERTO", "TRABAJANDO"):
        flash("No puede adjuntar un archivo a un ticket que no está abierto o trabajando.", "warning")
        return redirect(detalle_url)
    funcionario = _get_funcionario_from_current_user()
    form = SoporteAdjuntoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        # Validar la descripción
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es requerida.", "warning")
            es_valido = False
        # Validar el archivo
        archivo = request.files["archivo"]
        storage = GoogleCloudStorage(SUBDIRECTORIO)
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Insertar el registro, para obtener el ID
            cit_archivo = SoporteAdjunto(
                soporte_ticket=ticket,
                descripcion=descripcion,
            )
            cit_archivo.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=cit_archivo.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                cit_archivo.archivo = archivo.filename  # Conservar el nombre original
                cit_archivo.url = storage.url
                cit_archivo.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception:
                flash("Error al subir el archivo.", "danger")
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Subida de archivo {cit_archivo.archivo} al ticket {ticket.id} por {funcionario.nombre}."),
                url=detalle_url,
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.usuario.data = ticket.usuario.nombre  # Read only
    form.problema.data = ticket.descripcion  # Read only
    form.categoria.data = ticket.soporte_categoria.nombre  # Read only
    return render_template("soportes_adjuntos/new.jinja2", form=form, soporte_ticket=ticket)
