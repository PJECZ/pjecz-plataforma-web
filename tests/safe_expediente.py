"""
Testing lib/safe_string.py safe_expediente function
"""
import re
import unittest

from lib.safe_string import EXPEDIENTE_REGEXP, safe_expediente


class TestSafeExpediente(unittest.TestCase):
    """Test Safe Expediente"""

    strings = [
        ("123/2020", "123/2020"),
        ("   123/2020", "123/2020"),
        ("1/2020  ", "1/2020"),
        ("1/2020-II", "1/2020-II"),
        ("1/2020-III", "1/2020-III"),
    ]

    def test_safe_expediente(self):
        """Test Safe Expediente"""

        for string, expected in self.strings:
            try:
                clean_reg_exp = safe_expediente(string)
            except (IndexError, ValueError):
                self.assertEqual(True, False)
            self.assertEqual(re.match(EXPEDIENTE_REGEXP, clean_reg_exp) is not None, True)


if __name__ == "__main__":
    unittest.main()
