"""
Financieros Vales Adjuntos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.fin_vales.models import FinVale
from plataforma_web.blueprints.fin_vales_adjuntos.models import FinValeAdjunto
from plataforma_web.blueprints.fin_vales_adjuntos.forms import FinValeAdjuntoForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "FIN VALES ADJUNTOS"
SUBDIRECTORIO = "fin_vales_adjuntos"

fin_vales_adjuntos = Blueprint("fin_vales_adjuntos", __name__, template_folder="templates")


@fin_vales_adjuntos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@fin_vales_adjuntos.route("/fin_vales_adjuntos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Adjuntos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = FinValeAdjunto.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "fin_vale_id" in request.form:
        consulta = consulta.filter_by(fin_vale_id=request.form["fin_vale_id"])
    registros = consulta.order_by(FinValeAdjunto.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("fin_vales_adjuntos.detail", fin_vale_adjunto_id=resultado.id),
                },
                "tipo": resultado.tipo,
                "vinculo": {
                    "archivo": resultado.archivo,
                    "url": resultado.url,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@fin_vales_adjuntos.route("/fin_vales_adjuntos/<int:fin_vale_adjunto_id>")
def detail(fin_vale_adjunto_id):
    """Detalle de un Adjunto"""
    fin_vale_adjunto = FinValeAdjunto.query.get_or_404(fin_vale_adjunto_id)
    return render_template("fin_vales_adjuntos/detail.jinja2", fin_vale_adjunto=fin_vale_adjunto)


@fin_vales_adjuntos.route("/fin_vales_adjuntos/nuevo/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(fin_vale_id):
    """Nuevo Adjunto"""
    # Consultar y validar el vale
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus != "A":
        flash("No puede adjuntar un archivo a un vale eliminado.", "warning")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    if fin_vale.estado not in ["AUTORIZADO", "COMPROBADO"]:
        flash("No puede adjuntar un archivo a un vale que no esta autorizado o comprobado.", "warning")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    if not (current_user.can_admin(MODULO) or fin_vale.usuario == current_user):
        flash("No puede adjuntar un archivo a un vale si no fue creado por Usted.", "warning")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeAdjuntoForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        # Definir la descripcion que formara parte del nombre del archivo a subir
        tipo = form.tipo.data
        descripcion = safe_string(f"Vale {fin_vale_id} Tipo {tipo}")
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
            fin_vale_adjunto = FinValeAdjunto(
                fin_vale=fin_vale,
                tipo=form.tipo.data,
            )
            fin_vale_adjunto.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=fin_vale_adjunto.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                fin_vale_adjunto.archivo = archivo.filename  # Conservar el nombre original
                fin_vale_adjunto.url = storage.url
                fin_vale_adjunto.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception:
                flash("Error al subir el archivo.", "danger")
            # Cambiar el estado del vale
            if fin_vale.estado == "AUTORIZADO":
                fin_vale.estado = "COMPROBADO"
                fin_vale.save()
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo adjunto en vales {fin_vale_adjunto.archivo}"),
                url=url_for("fin_vales.detail", fin_vale_id=fin_vale_id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.fin_vale_usuario_nombre.data = fin_vale.usuario.nombre
    form.fin_vale_tipo.data = fin_vale.tipo
    form.fin_vale_justificacion.data = fin_vale.justificacion
    form.fin_vale_monto.data = fin_vale.monto
    form.tipo.data = "FACTURA PDF"
    return render_template("fin_vales_adjuntos/new.jinja2", form=form, fin_vale=fin_vale)
