"""
Testing lib/safe_string.py safe_expediente function
"""
import unittest

from lib.safe_string import safe_expediente


class TestSafeExpediente(unittest.TestCase):
    """Test Safe Expediente"""

    strings = [
        ("1/2020", "1/2020"),
        ("12/2020", "12/2020"),
        ("123/2020", "123/2020"),
        ("1/2020-II", "1/2020-II"),
        ("1/2020-II-2", "1/2020-II-2"),
        ("1/2020-F2", "1/2020-F2"),
    ]

    def test_safe_expediente(self):
        """Test Safe Expediente"""

        for string, expected in self.strings:
            self.assertEqual(safe_expediente(string), expected)


if __name__ == "__main__":
    unittest.main()
