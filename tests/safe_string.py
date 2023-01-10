"""
Testing lib/safe_string.py
"""
import unittest

from lib.safe_string import safe_string


class TestSafeString(unittest.TestCase):

    strings = [
        ("Distrito Judicial de Acuña", "DISTRITO JUDICIAL DE ACUÑA"),
        ("Distrito Judicial de Monclova", "DISTRITO JUDICIAL DE MONCLOVA"),
        ("Distrito Judicial de Parras de la Fuente", "DISTRITO JUDICIAL DE PARRAS DE LA FUENTE"),
        ("Distrito Judicial de Río Grande (Piedras Negras)", "DISTRITO JUDICIAL DE RIO GRANDE (PIEDRAS NEGRAS)"),
        ("Distrito Judicial de la Región Carbonífera", "DISTRITO JUDICIAL DE LA REGION CARBONIFERA"),
        ("Distrito Judicial de Saltillo", "DISTRITO JUDICIAL DE SALTILLO"),
        ("Distrito Judicial de San Pedro de las Colonias", "DISTRITO JUDICIAL DE SAN PEDRO DE LAS COLONIAS"),
        ("Distrito Judicial de Torreón", "DISTRITO JUDICIAL DE TORREON"),
        ("Órganos No Jurisdiccionales", "ORGANOS NO JURISDICCIONALES"),
        ("Presidencia", "PRESIDENCIA"),
        ("Administrativo", "ADMINISTRATIVO"),
        ("Órganos Jurisdiccionales", "ORGANOS JURISDICCIONALES"),
        ("Consejo de la Judicatura", "CONSEJO DE LA JUDICATURA"),
        ("Salas", "SALAS"),
        ("Pleno del Tribunal Constitucional", "PLENO DEL TRIBUNAL CONSTITUCIONAL"),
        ("Pleno del Tribunal Superior de Justicia", "PLENO DEL TRIBUNAL SUPERIOR DE JUSTICIA"),
        ("Tribunales Distritales", "TRIBUNALES DISTRITALES"),
        ("Órganos Especializados", "ORGANOS ESPECIALIZADOS"),
        ("NO DEFINIDO", "NO DEFINIDO"),
        ("Tribunales Laborales", "TRIBUNALES LABORALES"),
        ("Acuña", "ACUÑA"),
        ("Monclova", "MONCLOVA"),
        ("Parras", "PARRAS"),
        ("Río Grande", "RIO GRANDE"),
        ("Región Carbonífera", "REGION CARBONIFERA"),
        ("Saltillo", "SALTILLO"),
        ("San Pedro", "SAN PEDRO"),
        ("Torreón", "TORREON"),
        ("O. No Jurisdiccionales", "O. NO JURISDICCIONALES"),
        ("Presidencia", "PRESIDENCIA"),
        ("Administrativo", "ADMINISTRATIVO"),
        ("O. Jurisdiccionales", "O. JURISDICCIONALES"),
        ("Consejo", "CONSEJO"),
        ("Salas", "SALAS"),
        ("Tribunal Constitucional", "TRIBUNAL CONSTITUCIONAL"),
        ("Tribunal Superior", "TRIBUNAL SUPERIOR"),
        ("T. Distritales", "T. DISTRITALES"),
        ("O. Especializados", "O. ESPECIALIZADOS"),
        ("NO DEFINIDO", "NO DEFINIDO"),
        ("T. Laborales", "T. LABORALES"),
        ("Acentos áéíóúñ y ÁÉÍÓÚÑ.", "ACENTOS AEIOUÑ Y AEIOUÑ."),
    ]

    string_sin_enie = [
        ("Acentos áéíóúñ y ÁÉÍÓÚÑ.", "ACENTOS AEIOUN Y AEIOUN."),
    ]

    def test_safe_string(self):
        for string, expected in self.strings:
            self.assertEqual(safe_string(string, do_unidecode=True, save_enie=True), expected)

    def test_safe_string_sin_enie(self):
        for string, expected in self.string_sin_enie:
            self.assertEqual(safe_string(string, do_unidecode=True), expected)


if __name__ == "__main__":
    unittest.main()
