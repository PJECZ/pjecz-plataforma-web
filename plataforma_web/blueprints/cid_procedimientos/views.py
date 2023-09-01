"""
CID Procedimientos, vistas
"""
import json
from delta import html
from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_email, safe_string, safe_message

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_procedimientos.forms import CIDProcedimientoForm, CIDProcedimientoAcceptRejectForm, CIDProcedimientoEditAdminForm, CIDProcedimientoSearchForm
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")

MODULO = "CID PROCEDIMIENTOS"

# Roles que deben estar en la base de datos
ROL_COORDINADOR = "SICGD COORDINADOR"
ROL_DIRECTOR_JEFE = "SICGD DIRECTOR O JEFE"
ROL_DUENO_PROCESO = "SICGD DUENO DE PROCESO"
ROL_INVOLUCRADO = "SICGD INVOLUCRADO"


@cid_procedimientos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_procedimientos.route("/cid_procedimientos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cid Procedimientos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CIDProcedimiento.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter(CIDProcedimiento.usuario_id == request.form["usuario_id"])
    if "seguimiento" in request.form:
        consulta = consulta.filter(CIDProcedimiento.seguimiento == request.form["seguimiento"])
    if "seguimiento_filtro" in request.form:
        consulta = consulta.filter(CIDProcedimiento.seguimiento.contains(request.form["seguimiento_filtro"]))
    if "fecha_desde" in request.form:
        consulta = consulta.filter(CIDProcedimiento.creado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(CIDProcedimiento.creado <= request.form["fecha_hasta"])
    if "titulo_procedimiento" in request.form:
        consulta = consulta.filter(CIDProcedimiento.titulo_procedimiento.contains(safe_string(request.form["titulo_procedimiento"])))
    if "codigo" in request.form:
        consulta = consulta.filter(CIDProcedimiento.codigo.contains(safe_string(request.form["codigo"])))
    if "elaboro_nombre" in request.form:
        consulta = consulta.filter(CIDProcedimiento.elaboro_nombre.contains(safe_string(request.form["elaboro_nombre"])))
    registros = consulta.order_by(CIDProcedimiento.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("cid_procedimientos.detail", cid_procedimiento_id=resultado.id),
                },
                "titulo_procedimiento": resultado.titulo_procedimiento,
                "codigo": resultado.codigo,
                "revision": resultado.revision,
                "elaboro_nombre": resultado.elaboro_email,
                "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                "seguimiento": resultado.seguimiento,
                "seguimiento_posterior": resultado.seguimiento_posterior,
                "usuario": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "autoridad": resultado.autoridad.clave,
                "cid_area": {
                    "clave": resultado.cid_area.clave,
                    "url": url_for("cid_areas.detail", cid_area_id=resultado.cid_area_id) if current_user.can_view("CID AREAS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cid_procedimientos.route("/cid_procedimientos")
def list_active():
    """Listado por defecto de Procedimientos"""
    # Si es administrador, mostrar todos los procedimientos
    if current_user.can_admin(MODULO):
        return render_template(
            "cid_procedimientos/list_admin.jinja2",
            titulo="Todos los Procedimientos",
            filtros=json.dumps({"estatus": "A"}),
            estatus="A",
            show_button_list_owned=True,
            show_button_list_all=True,
        )

    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Mostrar solo los procedimientos del area en la que estoy
    # Mostrar solo los procedimientos autorizados
    return render_template(
        "cid_procedimientos/list.jinja2",
        titulo="Procedimientos autorizados",
        filtros=json.dumps({"estatus": "A", "seguimiento": "AUTORIZADO"}),
        estatus="A",
        show_button_list_owned=ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles,
        show_button_list_all=ROL_COORDINADOR in current_user_roles,
    )


@cid_procedimientos.route("/cid_procedimientos/autorizados")
def list_authorized():
    """Listado de Procedimientos autorizados"""
    current_user_roles = current_user.get_roles()
    return render_template(
        "cid_procedimientos/list.jinja2",
        titulo="Procedimientos autorizados",
        filtros=json.dumps({"estatus": "A", "seguimiento": "AUTORIZADO"}),
        estatus="A",
        show_button_list_owned=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles,
        show_button_list_all=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles,
    )


@cid_procedimientos.route("/cid_procedimientos/propios")
def list_owned():
    """Listado de Procedimientos propios"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador, coordinador, director o jefe o dueno de proceso, mostrar los procedimientos propios
    if current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles:
        return render_template(
            "cid_procedimientos/list.jinja2",
            titulo="Procedimientos propios",
            filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
            estatus="A",
            show_button_list_owned=True,
            show_button_list_all=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles,
        )
    # Si no, redirigir a la lista general
    return redirect(url_for("cid_procedimientos.list_active"))


@cid_procedimientos.route("/cid_procedimientos/todos")
def list_all():
    """Listado de Todos los Procedimientos"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador, coordinador, mostrar todos los procedimientos
    if current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles:
        return render_template(
            "cid_procedimientos/list.jinja2",
            titulo="Todos los Procedimientos",
            filtros=json.dumps({"estatus": "A"}),
            estatus="A",
            show_button_list_owned=True,
            show_button_list_all=True,
        )
    # Si no, redirigir a la lista general
    return redirect(url_for("cid_procedimientos.list_active"))


@cid_procedimientos.route("/cid_procedimientos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Procedimientos propios eliminados"""
    return render_template(
        "cid_procedimientos/list.jinja2",
        titulo="Procedimientos propios eliminados",
        filtros=json.dumps({"estatus": "B", "usuario_id": current_user.id}),
        estatus="B",
        show_button_list_owned=True,
        show_button_list_all=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user.get_roles(),
    )


@cid_procedimientos.route("/cid_procedimientos/<int:cid_procedimiento_id>")
def detail(cid_procedimiento_id):
    """Detalle de un CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    cid_formatos = CIDFormato.query.filter(CIDFormato.procedimiento == cid_procedimiento).filter(CIDFormato.estatus == "A").order_by(CIDFormato.id).all()
    return render_template(
        "cid_procedimientos/detail.jinja2",
        cid_procedimiento=cid_procedimiento,
        firma_al_vuelo=cid_procedimiento.elaborar_firma(),
        objetivo=str(html.render(cid_procedimiento.objetivo["ops"])),
        alcance=str(html.render(cid_procedimiento.alcance["ops"])),
        documentos=str(html.render(cid_procedimiento.documentos["ops"])),
        definiciones=str(html.render(cid_procedimiento.definiciones["ops"])),
        responsabilidades=str(html.render(cid_procedimiento.responsabilidades["ops"])),
        desarrollo=str(html.render(cid_procedimiento.desarrollo["ops"])),
        registros=cid_procedimiento.registros,
        control_cambios=cid_procedimiento.control_cambios,
        cid_formatos=cid_formatos,
        show_button_edit_admin=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user.get_roles(),
    )


@cid_procedimientos.route("/cid_procedimientos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo CID Procedimiento"""
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        elaboro = form.elaboro_email.data
        if elaboro is None:
            elaboro_nombre = ""
            elaboro_email = ""
        else:
            elaboro_nombre = form.elaboro_nombre.data
            elaboro_email = elaboro
        reviso = form.reviso_email.data
        if reviso is None:
            reviso_nombre = ""
            reviso_email = ""
        else:
            reviso_nombre = form.reviso_nombre.data
            reviso_email = reviso
        aprobo = form.aprobo_email.data
        if aprobo is None:
            aprobo_nombre = ""
            aprobo_email = ""
        else:
            aprobo_nombre = form.aprobo_nombre.data
            aprobo_email = aprobo
        registros_data = form.registros.data
        if registros_data is None:
            registros = {}
        else:
            registros = registros_data
        control = form.control_cambios.data
        if control is None:
            control_cambios = {}
        else:
            control_cambios = control
        cid_procedimiento = CIDProcedimiento(
            autoridad=current_user.autoridad,
            usuario=current_user,
            titulo_procedimiento=safe_string(form.titulo_procedimiento.data),
            codigo=form.codigo.data,
            revision=form.revision.data,
            fecha=form.fecha.data,
            objetivo=form.objetivo.data,
            alcance=form.alcance.data,
            documentos=form.documentos.data,
            definiciones=form.definiciones.data,
            responsabilidades=form.responsabilidades.data,
            desarrollo=form.desarrollo.data,
            registros=registros,
            elaboro_nombre=safe_string(elaboro_nombre, save_enie=True),
            elaboro_puesto=safe_string(form.elaboro_puesto.data),
            elaboro_email=safe_email(elaboro_email),
            reviso_nombre=safe_string(reviso_nombre, save_enie=True),
            reviso_puesto=safe_string(form.reviso_puesto.data),
            reviso_email=safe_email(reviso_email),
            aprobo_nombre=safe_string(aprobo_nombre, save_enie=True),
            aprobo_puesto=safe_string(form.aprobo_puesto.data),
            aprobo_email=safe_email(aprobo_email),
            control_cambios=control_cambios,
            cadena=0,
            seguimiento="EN ELABORACION",
            seguimiento_posterior="EN ELABORACION",
            anterior_id=0,
            firma="",
            archivo="",
            url="",
            cid_area_id=1,
        )
        cid_procedimiento.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Procedimiento {cid_procedimiento.titulo_procedimiento}"),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("cid_procedimientos/new.jinja2", form=form, help_quill=help_quill("new"))


@cid_procedimientos.route("/cid_procedimientos/edicion/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cid_procedimiento_id):
    """Editar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede editarlo
    if cid_procedimiento.seguimiento not in ["EN ELABORACION", "EN REVISION", "EN AUTORIZACION"]:
        flash(f"No puede editar porque su seguimiento es {cid_procedimiento.seguimiento} y ha sido FIRMADO. ", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))
    form = CIDProcedimientoForm()
    if form.validate_on_submit():
        elaboro = form.elaboro_email.data
        if elaboro is None or elaboro == "":
            elaboro_nombre = ""
            elaboro_email = ""
        else:
            elaboro_nombre = form.elaboro_nombre.data
            elaboro_email = elaboro
        reviso = form.reviso_email.data
        if reviso is None or reviso == "":
            reviso_nombre = ""
            reviso_email = ""
        else:
            reviso_nombre = form.reviso_nombre.data
            reviso_email = reviso
        aprobo = form.aprobo_email.data
        if aprobo is None or aprobo == "":
            aprobo_nombre = ""
            aprobo_email = ""
        else:
            aprobo_nombre = form.aprobo_nombre.data
            aprobo_email = aprobo
        registro = form.registros.data
        if registro is None:
            registros = {}
        else:
            registros = registro
        control = form.control_cambios.data
        if control is None:
            control_cambios = {}
        else:
            control_cambios = control
        cid_procedimiento.titulo_procedimiento = safe_string(form.titulo_procedimiento.data)
        cid_procedimiento.codigo = form.codigo.data
        cid_procedimiento.revision = form.revision.data
        cid_procedimiento.fecha = form.fecha.data
        cid_procedimiento.objetivo = form.objetivo.data
        cid_procedimiento.alcance = form.alcance.data
        cid_procedimiento.documentos = form.documentos.data
        cid_procedimiento.definiciones = form.definiciones.data
        cid_procedimiento.responsabilidades = form.responsabilidades.data
        cid_procedimiento.desarrollo = form.desarrollo.data
        cid_procedimiento.registros = registros
        cid_procedimiento.elaboro_nombre = safe_string(elaboro_nombre, save_enie=True)
        cid_procedimiento.elaboro_puesto = safe_string(form.elaboro_puesto.data)
        cid_procedimiento.elaboro_email = safe_email(elaboro_email)
        cid_procedimiento.reviso_nombre = safe_string(reviso_nombre, save_enie=True)
        cid_procedimiento.reviso_puesto = safe_string(form.reviso_puesto.data)
        cid_procedimiento.reviso_email = safe_email(reviso_email)
        cid_procedimiento.aprobo_nombre = safe_string(aprobo_nombre, save_enie=True)
        cid_procedimiento.aprobo_puesto = safe_string(form.aprobo_puesto.data)
        cid_procedimiento.aprobo_email = safe_email(aprobo_email)
        cid_procedimiento.control_cambios = control_cambios
        cid_procedimiento.cid_area_id = 1
        cid_procedimiento.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Definir los valores de los campos del formulario
    form.titulo_procedimiento.data = cid_procedimiento.titulo_procedimiento
    form.codigo.data = cid_procedimiento.codigo
    form.revision.data = cid_procedimiento.revision
    form.fecha.data = cid_procedimiento.fecha
    form.objetivo.data = cid_procedimiento.objetivo
    form.alcance.data = cid_procedimiento.alcance
    form.documentos.data = cid_procedimiento.documentos
    form.definiciones.data = cid_procedimiento.definiciones
    form.responsabilidades.data = cid_procedimiento.responsabilidades
    form.desarrollo.data = cid_procedimiento.desarrollo
    form.registros.data = cid_procedimiento.registros
    form.elaboro_nombre.data = cid_procedimiento.elaboro_nombre
    form.elaboro_puesto.data = cid_procedimiento.elaboro_puesto
    form.elaboro_email.data = cid_procedimiento.elaboro_email
    form.reviso_nombre.data = cid_procedimiento.reviso_nombre
    form.reviso_puesto.data = cid_procedimiento.reviso_puesto
    form.reviso_email.data = cid_procedimiento.reviso_email
    form.aprobo_nombre.data = cid_procedimiento.aprobo_nombre
    form.aprobo_puesto.data = cid_procedimiento.aprobo_puesto
    form.aprobo_email.data = cid_procedimiento.aprobo_email
    form.control_cambios.data = cid_procedimiento.control_cambios
    # Para cargar el contenido de los QuillJS hay que convertir a JSON válido (por ejemplo, cambia True por true)
    objetivo_json = json.dumps(cid_procedimiento.objetivo)
    alcance_json = json.dumps(cid_procedimiento.alcance)
    documentos_json = json.dumps(cid_procedimiento.documentos)
    definiciones_json = json.dumps(cid_procedimiento.definiciones)
    responsabilidades_json = json.dumps(cid_procedimiento.responsabilidades)
    desarrollo_json = json.dumps(cid_procedimiento.desarrollo)
    registros_json = json.dumps(cid_procedimiento.registros)
    control_cambios_json = json.dumps(cid_procedimiento.control_cambios)
    return render_template(
        "cid_procedimientos/edit.jinja2",
        form=form,
        cid_procedimiento=cid_procedimiento,
        objetivo_json=objetivo_json,
        alcance_json=alcance_json,
        documentos_json=documentos_json,
        definiciones_json=definiciones_json,
        responsabilidades_json=responsabilidades_json,
        desarrollo_json=desarrollo_json,
        registros_json=registros_json,
        control_cambios_json=control_cambios_json,
        help_quill=help_quill("edit"),
    )


@cid_procedimientos.route("/cid_procedimientos/clasificar/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_admin(cid_procedimiento_id):
    """Clasificar Procedimiento"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si NO es administrador o coordinador, redirigir a la edicion normal
    if not (current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles):
        return redirect(url_for("cid_procedimientos.edit", cid_procedimiento_id=cid_procedimiento_id))
    # Consultar el Procedimiento
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    # Si viene el formulario
    form = CIDProcedimientoEditAdminForm()
    if form.validate_on_submit():
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        cid_procedimiento.autoridad = autoridad
        cid_procedimiento.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Clasificado el Procedimiento {cid_procedimiento.id} con autoridad {autoridad.clave}"),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Mostrar el formulario
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()  # Combo distritos-autoridades
    autoridades = Autoridad.query.filter_by(estatus="A").order_by(Autoridad.clave).all()  # Combo distritos-autoridades
    form.titulo_procedimiento.data = cid_procedimiento.titulo_procedimiento
    form.codigo.data = cid_procedimiento.codigo
    form.revision.data = cid_procedimiento.revision
    return render_template(
        "cid_procedimientos/edit_admin.jinja2",
        form=form,
        cid_procedimiento=cid_procedimiento,
        distritos=distritos,
        autoridades=autoridades,
    )


def validate_json_quill_not_empty(data):
    """Validar que un JSON de Quill no esté vacío"""
    if not isinstance(data, dict):
        return False
    if not "ops" in data:
        return False
    try:
        if data["ops"][0]["insert"].strip() == "":
            return False
        return True
    except KeyError:
        return False


@cid_procedimientos.route("/cid_procedimientos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Cid Procedimientos"""
    form_search = CIDProcedimientoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        # Si se busca por el ID y se encuentra, se redirecciona al detalle
        if form_search.id.data:
            cid_procedimiento_id = int(form_search.id.data)
            if cid_procedimiento_id != 0:
                cid_procedimiento = CIDProcedimiento.query.get(cid_procedimiento_id)
                if cid_procedimiento is not None:
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))
        # Si se busca con los demas parametros
        # if form_search.fecha_desde.data:
        #     busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
        #     titulos.append("fecha desde " + busqueda["fecha_desde"])
        # if form_search.fecha_hasta.data:
        #     busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
        #     titulos.append("fecha hasta " + busqueda["fecha_hasta"])
        if form_search.titulo_procedimiento.data:
            titulo_procedimiento = safe_string(form_search.titulo_procedimiento.data)
            if titulo_procedimiento != "":
                busqueda["titulo_procedimiento"] = titulo_procedimiento
                titulos.append("titulo_procedimiento " + titulo_procedimiento)
        if form_search.codigo.data:
            codigo = safe_string(form_search.codigo.data)
            if codigo != "":
                busqueda["codigo"] = codigo
                titulos.append("codigo " + codigo)
        if form_search.elaboro_nombre.data:
            elaboro_nombre = safe_string(form_search.elaboro_nombre.data, save_enie=True)
            if elaboro_nombre != "":
                busqueda["elaboro_nombre"] = elaboro_nombre
                titulos.append("elaboro_nombre " + elaboro_nombre)
        return render_template(
            "cid_procedimientos/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Cid Procedimientos con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("cid_procedimientos/search.jinja2", form=form_search)


@cid_procedimientos.route("/cid_procedimientos/firmar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def sign_for_maker(cid_procedimiento_id):
    """Firmar"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.usuario_id != current_user.id:
        abort(403)  # Acceso no autorizado, solo el propietario puede firmarlo
    # Validar objetivo
    objetivo_es_valido = validate_json_quill_not_empty(cid_procedimiento.objetivo)
    # Validar alcance
    alcance_es_valido = validate_json_quill_not_empty(cid_procedimiento.alcance)
    # Validar documentos
    documentos_es_valido = validate_json_quill_not_empty(cid_procedimiento.documentos)
    # Validar definiciones
    definiciones_es_valido = validate_json_quill_not_empty(cid_procedimiento.definiciones)
    # Validar responsabilidades
    responsabilidades_es_valido = validate_json_quill_not_empty(cid_procedimiento.responsabilidades)
    # Validar desarrollo
    desarrollo_es_valido = validate_json_quill_not_empty(cid_procedimiento.desarrollo)
    # Validar registros
    registros_es_valido = cid_procedimiento.registros
    # Validar control_cambios
    control_cambios_es_valido = cid_procedimiento.control_cambios
    # Validar elaboro
    elaboro_es_valido = False
    if cid_procedimiento.elaboro_email != "":
        elaboro = Usuario.query.filter_by(email=cid_procedimiento.elaboro_email).first()
        elaboro_es_valido = elaboro is not None  # TODO: Validar que tenga el rol SICGD DUENO DE PROCESO
    # Validar reviso
    reviso_es_valido = False
    if cid_procedimiento.reviso_email != "":
        reviso = Usuario.query.filter_by(email=cid_procedimiento.reviso_email).first()
        reviso_es_valido = reviso is not None  # TODO: Validar que tenga el rol SICGD DIRECTOR O JEFE
    # Validar autorizo
    aprobo_es_valido = False
    if cid_procedimiento.aprobo_email != "":
        aprobo = Usuario.query.filter_by(email=cid_procedimiento.aprobo_email).first()
        aprobo_es_valido = aprobo is not None  # TODO: Validar que tenga el rol SICGD DIRECTOR O JEFE
    # Poner barreras para prevenir que se firme si está incompleto
    if cid_procedimiento.firma != "":
        flash("Este procedimiento ya ha sido firmado.", "warning")
    elif not objetivo_es_valido:
        flash("Objetivo no pasa la validación.", "warning")
    elif not alcance_es_valido:
        flash("Alcance no pasa la validación.", "warning")
    elif not documentos_es_valido:
        flash("Documentos no pasa la validación.", "warning")
    elif not definiciones_es_valido:
        flash("Definiciones no pasa la validación.", "warning")
    elif not responsabilidades_es_valido:
        flash("Responsabilidades no pasa la validación.", "warning")
    elif not desarrollo_es_valido:
        flash("Desarrollo no pasa la validación.", "warning")
    elif not registros_es_valido:
        flash("Registros no pasa la validación.", "warning")
    elif not control_cambios_es_valido:
        flash("Control de Cambios no pasa la validación.", "warning")
    elif not elaboro_es_valido:
        flash("Quien elabora no pasa la validación.", "warning")
    elif not reviso_es_valido:
        flash("Quien revisa no pasa la validación.", "warning")
    elif not aprobo_es_valido:
        flash("Quien aprueba no pasa la validación.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="cid_procedimientos.tasks.crear_pdf",
            descripcion=f"Crear archivo PDF de {cid_procedimiento.titulo_procedimiento}",
            usuario_id=current_user.id,
            cid_procedimiento_id=cid_procedimiento.id,
            accept_reject_url=url_for("cid_procedimientos.accept_reject", cid_procedimiento_id=cid_procedimiento.id),
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id))


@cid_procedimientos.route("/cid_procedimientos/aceptar_rechazar/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def accept_reject(cid_procedimiento_id):
    """Aceptar o Rechazar un Procedimiento"""
    original = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    # Validar que NO haya sido eliminado
    if original.estatus != "A":
        flash("Este procedimiento no es activo.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    # Validar que este procedimiento este elaborado o revisado
    if not original.seguimiento in ["ELABORADO", "REVISADO"]:
        flash("Este procedimiento no puede ser aceptado.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    # Validar que NO haya sido YA aceptado
    if original.seguimiento_posterior in ["EN REVISION", "EN AUTORIZACION"]:
        flash("Este procedimiento ya fue aceptado.", "warning")
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    form = CIDProcedimientoAcceptRejectForm()
    if form.validate_on_submit():
        # Si fue aceptado
        if form.aceptar.data is True:
            # Deberian definirse estos campos
            nuevo_seguimiento = None
            nuevo_seguimiento_posterior = None
            nuevo_usuario = None
            # Si este procedimiento fue elaborado, sigue revisarlo
            if original.seguimiento == "ELABORADO":
                usuario = Usuario.query.filter_by(email=original.reviso_email).first()
                if usuario is None:
                    flash(f"No fue encontrado el usuario con e-mail {original.reviso_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
                nuevo_seguimiento = "EN REVISION"
                nuevo_seguimiento_posterior = "EN REVISION"
                nuevo_usuario = usuario
            # Si este procedimiento fue revisado, sigue autorizarlo
            if original.seguimiento == "REVISADO":
                usuario = Usuario.query.filter_by(email=original.aprobo_email).first()
                if usuario is None:
                    flash(f"No fue encontrado el usuario con e-mail {original.aprobo_email}", "danger")
                    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
                nuevo_seguimiento = "EN AUTORIZACION"
                nuevo_seguimiento_posterior = "EN AUTORIZACION"
                nuevo_usuario = usuario
            # Validar que se hayan definido estos campos
            if nuevo_seguimiento is None:
                flash("No se definio el seguimiento.", "danger")
                return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
            if nuevo_seguimiento_posterior is None:
                flash("No se definio el seguimiento posterior.", "danger")
                return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
            if nuevo_usuario is None:
                flash("No se definio el usuario.", "danger")
                return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
            # Crear un nuevo registro
            nuevo = CIDProcedimiento(
                autoridad=original.autoridad,
                usuario=nuevo_usuario,
                titulo_procedimiento=safe_string(original.titulo_procedimiento),
                codigo=original.codigo,
                revision=original.revision,
                fecha=original.fecha,
                objetivo=original.objetivo,
                alcance=original.alcance,
                documentos=original.documentos,
                definiciones=original.definiciones,
                responsabilidades=original.responsabilidades,
                desarrollo=original.desarrollo,
                registros=original.registros,
                elaboro_nombre=original.elaboro_nombre,
                elaboro_puesto=original.elaboro_puesto,
                elaboro_email=original.elaboro_email,
                reviso_nombre=original.reviso_nombre,
                reviso_puesto=original.reviso_puesto,
                reviso_email=original.reviso_email,
                aprobo_nombre=original.aprobo_nombre,
                aprobo_puesto=original.aprobo_puesto,
                aprobo_email=original.aprobo_email,
                control_cambios=original.control_cambios,
                seguimiento=nuevo_seguimiento,
                seguimiento_posterior=nuevo_seguimiento_posterior,
                cadena=original.cadena + 1,
                anterior_id=original.id,
                firma="",
                archivo="",
                url="",
                cid_area_id=1,
            ).save()
            # Actualizar el anterior
            if original.seguimiento == "ELABORADO":
                # Cambiar el seguimiento posterior del procedimiento elaborado
                anterior = CIDProcedimiento.query.get(cid_procedimiento_id)
                anterior.seguimiento_posterior = "EN REVISION"
                anterior.save()
            if original.seguimiento == "REVISADO":
                # Cambiar el seguimiento posterior del procedimiento revisado
                anterior = CIDProcedimiento.query.get(cid_procedimiento_id)
                anterior.seguimiento_posterior = "EN AUTORIZACION"
                anterior.save()
            # Duplicar los formatos del procedimiento anterior a éste que es el nuevo
            if original.seguimiento == "ELABORADO" or original.seguimiento == "REVISADO":
                for cid_formato in anterior.formatos:
                    CIDFormato(
                        procedimiento=nuevo,
                        descripcion=cid_formato.descripcion,
                        archivo=cid_formato.archivo,
                        url=cid_formato.url,
                        cid_area_id=1,
                    ).save()
            # Bitacora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Aceptado el Procedimiento {nuevo.titulo_procedimiento}."),
                url=url_for("cid_procedimientos.detail", cid_procedimiento_id=nuevo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        # Fue rechazado
        if form.rechazar.data is True:
            # Preguntar porque fue rechazado
            flash("Usted ha rechazado revisar/autorizar este procedimiento.", "success")
        # Ir al detalle del procedimiento
        return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=original.id))
    # Mostrar el formulario
    form.titulo_procedimiento.data = original.titulo_procedimiento
    form.codigo.data = original.codigo
    form.revision.data = original.revision
    form.seguimiento.data = original.seguimiento
    form.seguimiento_posterior.data = original.seguimiento_posterior
    form.elaboro_nombre.data = original.elaboro_nombre
    form.reviso_nombre.data = original.reviso_nombre
    form.url.data = original.url
    return render_template("cid_procedimientos/accept_reject.jinja2", form=form, cid_procedimiento=original)


@cid_procedimientos.route("/cid_procedimientos/eliminar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cid_procedimiento_id):
    """Eliminar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede eliminarlo
    if not (current_user.can_admin(MODULO) or cid_procedimiento.seguimiento in ["EN ELABORACION", "EN REVISION", "EN AUTORIZACION"]):
        flash(f"No puede eliminarlo porque su seguimiento es {cid_procedimiento.seguimiento}.")
    elif cid_procedimiento.estatus == "A":
        if cid_procedimiento.seguimiento == "EN ELABORACION":
            cid_procedimiento.seguimiento = "CANCELADO POR ELABORADOR"
        elif cid_procedimiento.seguimiento == "EN REVISION":
            cid_procedimiento.seguimiento = "CANCELADO POR REVISOR"
        elif cid_procedimiento.seguimiento == "EN AUTORIZACION":
            cid_procedimiento.seguimiento = "CANCELADO POR AUTORIZADOR"
        cid_procedimiento.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


@cid_procedimientos.route("/cid_procedimientos/recuperar/<int:cid_procedimiento_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(cid_procedimiento_id):
    """Recuperar CID Procedimiento"""
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if not (current_user.can_admin(MODULO) or cid_procedimiento.usuario_id == current_user.id):
        abort(403)  # Acceso no autorizado, solo administradores o el propietario puede recuperarlo
    if not (current_user.can_admin(MODULO) or cid_procedimiento.seguimiento in ["CANCELADO POR ELABORADOR", "CANCELADO POR REVISOR", "CANCELADO POR AUTORIZADOR"]):
        flash(f"No puede recuperarlo porque su seguimiento es {cid_procedimiento.seguimiento}.")
    elif cid_procedimiento.estatus == "B":
        if cid_procedimiento.seguimiento == "CANCELADO POR ELABORADOR":
            cid_procedimiento.seguimiento = "EN ELABORACION"
        elif cid_procedimiento.seguimiento == "CANCELADO POR REVISOR":
            cid_procedimiento.seguimiento = "EN REVISION"
        elif cid_procedimiento.seguimiento == "CANCELADO POR AUTORIZADOR":
            cid_procedimiento.seguimiento = "EN AUTORIZACION"
        cid_procedimiento.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Procedimiento {cid_procedimiento.titulo_procedimiento}."),
            url=url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_procedimientos.detail", cid_procedimiento_id=cid_procedimiento_id))


def help_quill(seccion: str):
    """Cargar archivo de ayuda"""
    archivo_ayuda = open("plataforma_web/static/json/help/quill_help.json", "r")
    data = json.load(archivo_ayuda)
    archivo_ayuda.close()
    return render_template("quill_help.jinja2", titulo=data["titulo"], descripcion=data["descripcion"], secciones=data["secciones"], seccion_id=seccion)


@cid_procedimientos.route("/cid_procedimientos/usuarios_json", methods=["POST"])
def query_usuarios_json():
    """Proporcionar el JSON de usuarios para elegir con un Select2"""
    usuarios = Usuario.query.filter(Usuario.estatus == "A")
    if "searchString" in request.form:
        usuarios = usuarios.filter(Usuario.email.contains(safe_email(request.form["searchString"], search_fragment=True)))
    results = []
    for usuario in usuarios.order_by(Usuario.email).limit(10).all():
        results.append({"id": usuario.email, "text": usuario.email, "nombre": usuario.nombre})
    return {"results": results, "pagination": {"more": False}}


@cid_procedimientos.route("/cid_procedimientos/revisores_autorizadores_json", methods=["POST"])
def query_revisores_autorizadores_json():
    """Proporcionar el JSON de revisores para elegir con un Select2"""
    usuarios = Usuario.query.join(UsuarioRol, Rol).filter(Rol.nombre == ROL_DIRECTOR_JEFE)
    if "searchString" in request.form:
        usuarios = usuarios.filter(Usuario.email.contains(safe_email(request.form["searchString"], search_fragment=True)))
    usuarios = usuarios.filter(Usuario.estatus == "A")
    results = []
    for usuario in usuarios.order_by(Usuario.email).limit(10).all():
        results.append({"id": usuario.email, "text": usuario.email, "nombre": usuario.nombre})
    return {"results": results, "pagination": {"more": False}}
