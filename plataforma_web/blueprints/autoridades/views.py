"""
Autoridades, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades.forms import AutoridadNewForm, AutoridadEditForm
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.sentencias.models import Sentencia

autoridades = Blueprint("autoridades", __name__, template_folder="templates")

TARJETAS_LIMITE_REGISTROS = 5
MODULO = "AUTORIDADES"


@autoridades.before_request
@login_required
@permission_required(Permiso.VER_CATALOGOS)
def before_request():
    """Permiso por defecto"""


@autoridades.route("/autoridades")
def list_active():
    """Listado de Autoridades"""
    autoridades_activas = Autoridad.query.filter_by(estatus="A").all()
    return render_template("autoridades/list.jinja2", autoridades=autoridades_activas, estatus="A")


@autoridades.route("/autoridades/inactivas")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def list_inactive():
    """Listado de Autoridades inactivas"""
    autoridades_inactivas = Autoridad.query.filter_by(estatus="B").all()
    return render_template("autoridades/list.jinja2", autoridades=autoridades_inactivas, estatus="B")


@autoridades.route("/autoridades/<int:autoridad_id>")
def detail(autoridad_id):
    """Detalle de una Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    usuarios = Usuario.query.filter(Usuario.autoridad == autoridad).filter_by(estatus="A").all()
    return render_template("autoridades/detail.jinja2", autoridad=autoridad, usuarios=usuarios)


@autoridades.route("/autoridades/<int:autoridad_id>/audiencias_json", methods=["GET", "POST"])
def audiencias_json(autoridad_id):
    """Audiencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    # Filtrar por el dia de hoy
    audiencias = Audiencia.query.filter(Audiencia.autoridad == autoridad).filter_by(estatus="A").order_by(Audiencia.tiempo.desc())
    # Listado
    listado = []
    for audiencia in audiencias.limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "tiempo": audiencia.tiempo,
                "tipo_audiencia" "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
            }
        )
    # Total
    total = audiencias.count()
    if total > 0:
        breve = f"Tiene un total de {total} Audiencias agendadas."
    else:
        breve = "Nunca ha agendado Audiencias."
    # Entregar JSON
    return {
        "titulo": "Agenda de Audiencias",
        "breve": breve,
        "listado": [],
        "url": url_for("audiencias.list_autoridad_audiencias", autoridad_id=autoridad_id),
    }


@autoridades.route("/autoridades/<int:autoridad_id>/edictos_json", methods=["GET", "POST"])
def edictos_json(autoridad_id):
    """Edictos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    edictos = Edicto.query.filter(Edicto.autoridad == autoridad).filter_by(estatus="A").order_by(Edicto.creado.desc())
    # Listado
    listado = []
    for edicto in edictos.limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "expediente": edicto.expediente,
                "descripcion": edicto.descripcion,
                "url": url_for("edictos.detail", edicto_id=edicto.id),
            }
        )
    # Total
    total = edictos.count()
    if total > 0:
        breve = f"Tiene un total de {total} Edictos."
    else:
        breve = "Nunca a subido Edictos."
    # Entregar JSON
    return {
        "titulo": "Edictos",
        "breve": breve,
        "listado": listado,
        "url": url_for("edictos.list_autoridad_edictos", autoridad_id=autoridad_id),
    }


@autoridades.route("/autoridades/<int:autoridad_id>/listas_de_acuerdos_json", methods=["GET", "POST"])
def listas_de_acuerdos_json(autoridad_id):
    """Listas de Acuerdos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter_by(estatus="A").order_by(ListaDeAcuerdo.creado.desc())
    # Listado
    listado = []
    for lista_de_acuerdo in listas_de_acuerdos.limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
            }
        )
    # Total
    total = listas_de_acuerdos.count()
    if total > 0:
        breve = f"Tiene un total de {total} Listas de Acuerdos."
    else:
        breve = "Nunca a subido Listas de Acuerdos."
    # Entregar JSON
    return {
        "titulo": "Listas de Acuerdos",
        "breve": breve,
        "listado": listado,
        "url": url_for("listas_de_acuerdos.list_autoridad_listas_de_acuerdos", autoridad_id=autoridad_id),
    }


@autoridades.route("/autoridades/<int:autoridad_id>/sentencias_json", methods=["GET", "POST"])
def sentencias_json(autoridad_id):
    """Sentencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).filter_by(estatus="A").order_by(Sentencia.creado.desc())
    # Listado
    listado = []
    for sentencia in sentencias.limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "sentencia": sentencia.sentencia,
                "materia_tipo_juicio": sentencia.materia_tipo_juicio.descripcion,
                "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
            }
        )
    # Total
    total = sentencias.count()
    if total > 0:
        breve = f"Tiene un total de {total} V.P. de Sentencias."
    else:
        breve = "Nunca a subido V.P. de Sentencias."
    # Entregar JSON
    return {
        "titulo": "V.P. de Sentencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("sentencias.list_autoridad_sentencias", autoridad_id=autoridad_id),
    }


@autoridades.route("/autoridades/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CATALOGOS)
def new():
    """Nueva Autoridad"""
    form = AutoridadNewForm()
    if form.validate_on_submit():

        # Armar directorios
        distrito = form.distrito.data
        descripcion = form.descripcion.data.strip()
        es_jurisdiccional = form.es_jurisdiccional.data
        es_notaria = form.es_notaria.data
        directorio = f"{distrito.nombre}/{descripcion}"
        directorio_listas_de_acuerdos = ""
        directorio_sentencias = ""
        directorio_edictos = ""
        directorio_glosas = ""
        if es_jurisdiccional:
            directorio_edictos = directorio
            directorio_listas_de_acuerdos = directorio
            directorio_sentencias = directorio
            directorio_glosas = directorio
        if es_notaria:
            directorio_edictos = directorio

        # Insertar registro
        autoridad = Autoridad(
            distrito=distrito,
            descripcion=descripcion,
            descripcion_corta=form.descripcion_corta.data.strip(),
            clave=form.clave.data.strip().upper(),
            es_jurisdiccional=es_jurisdiccional,
            es_notaria=es_notaria,
            organo_jurisdiccional=form.organo_jurisdiccional.data,
            materia=form.materia.data,
            audiencia_categoria=form.audiencia_categoria.data,
            directorio_listas_de_acuerdos=directorio_listas_de_acuerdos,
            directorio_sentencias=directorio_sentencias,
            directorio_edictos=directorio_edictos,
            directorio_glosas=directorio_glosas,
        )
        autoridad.save()

        # Mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Nueva autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    return render_template("autoridades/new.jinja2", form=form)


@autoridades.route("/autoridades/edicion/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def edit(autoridad_id):
    """Editar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadEditForm()
    if form.validate_on_submit():
        autoridad.distrito = form.distrito.data
        autoridad.descripcion = form.descripcion.data.strip()
        autoridad.descripcion_corta = form.descripcion_corta.data.strip()
        autoridad.clave = form.clave.data.strip().upper()
        autoridad.es_jurisdiccional = form.es_jurisdiccional.data
        autoridad.es_notaria = form.es_notaria.data
        autoridad.organo_jurisdiccional = form.organo_jurisdiccional.data
        autoridad.materia = form.materia.data
        autoridad.audiencia_categoria = form.audiencia_categoria.data
        autoridad.directorio_listas_de_acuerdos = form.directorio_listas_de_acuerdos.data.strip()
        autoridad.directorio_sentencias = form.directorio_sentencias.data.strip()
        autoridad.directorio_edictos = form.directorio_edictos.data.strip()
        autoridad.directorio_glosas = form.directorio_glosas.data.strip()
        autoridad.save()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Editada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito
    form.descripcion.data = autoridad.descripcion
    form.descripcion_corta.data = autoridad.descripcion_corta
    form.clave.data = autoridad.clave
    form.es_jurisdiccional.data = autoridad.es_jurisdiccional
    form.es_notaria.data = autoridad.es_notaria
    form.organo_jurisdiccional.data = autoridad.organo_jurisdiccional
    form.materia.data = autoridad.materia
    form.audiencia_categoria.data = autoridad.audiencia_categoria
    form.directorio_listas_de_acuerdos.data = autoridad.directorio_listas_de_acuerdos
    form.directorio_sentencias.data = autoridad.directorio_sentencias
    form.directorio_edictos.data = autoridad.directorio_edictos
    form.directorio_glosas.data = autoridad.directorio_glosas
    return render_template("autoridades/edit.jinja2", form=form, autoridad=autoridad)


@autoridades.route("/autoridades/eliminar/<int:autoridad_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def delete(autoridad_id):
    """Eliminar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "A":
        autoridad.delete()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Eliminada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad_id))


@autoridades.route("/autoridades/recuperar/<int:autoridad_id>")
@permission_required(Permiso.MODIFICAR_CATALOGOS)
def recover(autoridad_id):
    """Recuperar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "B":
        autoridad.recover()
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message(f"Recuperada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad_id))
