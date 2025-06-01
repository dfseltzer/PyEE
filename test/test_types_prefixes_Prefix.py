import unittest
from pyee.types.prefixes import Prefix

class TestCase_from_string(unittest.TestCase):
    def test_from_string_symbol(self):
        test_sets = {"k": 1000}
        for pstring, value in test_sets.items():
            p = Prefix.from_string(pstring)
            self.assertEqual(p.f, value, msg=f"Testing for {pstring} = {value}")

    def test_from_string_name(self):
        test_sets = {"kilo": 1000}
        for pstring, value in test_sets.items():
            p = Prefix.from_string(pstring)
            self.assertEqual(p.f, value, msg=f"Testing for {pstring} = {value}")


class TestCase_from_number(unittest.TestCase):
    def test_from_number(self):
        test_sets = [[0.000015,"u"],
                     [0.0015,"m"],
                     [0.15,"m"],
                     [15,""],
                     [134.3,""],
                     [1215.2,"k"]]
        for number, symbol in test_sets:
            p = Prefix.from_number(number)
            self.assertEqual(p.s, symbol, msg=f"Testing for {number} = {symbol}")

    def test_from_number_edges(self):
        test_sets = [[999,""],
                     [1000,"k"],
                     [1001,"k"]]
        for number, symbol in test_sets:
            p = Prefix.from_number(number)
            self.assertEqual(p.s, symbol, msg=f"Testing for {number} = {symbol}")

    def test_from_number_negatives(self):
        test_sets = [[-0.000015,"u"],
                     [-0.0015,"m"],
                     [-0.15,"m"],
                     [-15,""],
                     [-134.3,""],
                     [-1215.2,"k"],
                     [-999,""],
                     [-1000,"k"],
                     [-1001,"k"]]
        for number, symbol in test_sets:
            p = Prefix.from_number(number)
            self.assertEqual(p.s, symbol, msg=f"Testing for {number} = {symbol}")

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
