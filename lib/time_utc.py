"""
Tiempo en UTC

Ejemplo
    from lib.time_utc import local_to_utc
    from datetime import datetime
    en_texto = "2021-08-13 10:00:00"
    tiempo = datetime.strptime(en_texto, "%Y-%m-%d %H:%M:%S")
    local_to_utc(tiempo)
"""
from datetime import datetime, date, time, timedelta
import pytz

LIMITE_DIAS = 30  # Cantidad de días al pasado y al futuro que se permiten
TIEMPO_DESDE = time(hour=8, minute=0, second=0)
TIEMPO_HASTA = time(hour=18, minute=0, second=0)
ZONA_HORARIA = pytz.timezone("America/Mexico_City")
ZONA_UTC = pytz.utc


def utc_to_local_str(tiempo: datetime):
    """Convertir de UTC a local"""
    local = ZONA_UTC.normalize(ZONA_UTC.localize(tiempo)).astimezone(ZONA_HORARIA)
    return local.strftime("%Y-%m-%d %H:%M:%S")


def local_to_utc(tiempo: datetime):
    """Convertir de local a UTC"""
    return ZONA_HORARIA.normalize(ZONA_HORARIA.localize(tiempo)).astimezone(ZONA_UTC)


def combine_to_utc(tiempo_fecha: date, tiempo_horas_minutos: time, validar_rango: bool = True):
    """Validar, combinar y cambiar un tiempo local a UTC"""

    # Validar tiempo_horas_minutos
    if validar_rango and not TIEMPO_DESDE <= tiempo_horas_minutos <= TIEMPO_HASTA:
        raise ValueError(f"La hora:minutos está fuera de rango. Debe ser entre {TIEMPO_DESDE.strftime('%H:%M')} y {TIEMPO_HASTA.strftime('%H:%M')}.")

    # Combinar
    combinado = datetime.combine(tiempo_fecha, tiempo_horas_minutos)

    # Validar que el tiempo esté dentro del rango permitido
    hoy = date.today()
    hoy_dt = datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    desde_dt = hoy_dt + timedelta(days=-LIMITE_DIAS)
    hasta_dt = hoy_dt + timedelta(days=LIMITE_DIAS)
    if validar_rango and not desde_dt <= combinado <= hasta_dt:
        raise ValueError(f"La fecha está fuera de rango. Debe ser entre {desde_dt.strftime('%Y-%m-%d')} y {hasta_dt.strftime('%Y-%m-%d')}.")

    # Entregar datetime en UTC
    return ZONA_HORARIA.normalize(ZONA_HORARIA.localize(combinado)).astimezone(pytz.utc)


def decombine_to_local(tiempo: datetime):
    """Descombinar un tiempo UTC a la fecha y hora local"""
    utc = pytz.utc.localize(tiempo)
    local = utc.astimezone(ZONA_HORARIA)
    return local.date(), local.time()


def join_for_message(tiempo_fecha: date, tiempo_horas_minutos: time):
    """Juntar fecha y hora:minuto para el mensaje"""
    return tiempo_fecha.strftime("%Y-%m-%d") + " " + tiempo_horas_minutos.strftime("%H:%M")
