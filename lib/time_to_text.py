"""
Tiempo a texto
"""
from datetime import date, datetime


MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def mes_en_palabra(mes_numero=None):
    """Entrega el nombre del mes"""
    if isinstance(mes_numero, int) and mes_numero in MESES:
        return MESES[mes_numero]
    hoy = date.today()
    return MESES[hoy.month]


def dia_mes_ano(fecha=None):
    """Entrega el dia en dos digitos, el mes en palabra y el año en cuatro digitos"""
    if isinstance(fecha, date) or isinstance(fecha, datetime):
        fecha_date = fecha
    elif isinstance(fecha, str) and fecha != "":
        fecha_date = datetime.strptime(fecha, "%Y-%m-%d")
    else:
        fecha_date = date.today()
    dia = "{:02d}".format(fecha_date.day)
    mes = mes_en_palabra(fecha_date.month)
    ano = str(fecha_date.year)
    return (dia, mes, ano)
