import unittest
from pyee.types.units import Units

class TestCase_from_string(unittest.TestCase):
    def test_create_empty_units_function(self):
        u = Units.create_unitless()
        self.assertDictEqual(u.s, {})

    def test_create_empty_units_string(self):
        empty_strs = ["1", "1/1", "1/(1)", "(1)/1", "s/s", "s.s^-1"]
        for ustring in empty_strs:
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, {})

    def test_create_empty_units_direct(self):
        u = Units({})
        self.assertDictEqual(u.s, {})

    def test_create_simple_1(self):
        # no demoninator, no paranthesis
        test_sets = {"m.s":{"m": 1, "s": 1},
                     "m.s^-1":{"m": 1, "s": -1},
                     "m^-1.s":{"m": -1, "s": 1},
                     "m.s.kg^2":{"m": 1, "s": 1, "kg":2}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_simple_2(self):
        # no demoninator, with parethesis
        test_sets = {"m.(s^1)":{"m": 1, "s": 1},
                     "m.(s)":{"m": 1, "s": 1},
                     "(m.s^-1)":{"m": 1, "s": -1},
                     "(m^-1).s":{"m": -1, "s": 1},
                     "m.(s).kg^2":{"m": 1, "s": 1, "kg":2}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_unit_denominator(self):
        # unit denominator and paranthensis
        test_sets = {"s/1":{"s": 1},
                     "s/(1)":{"s": 1},
                     "s^2/(1)":{"s": 2},
                     "s^-1/1":{"s": -1}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_unit_numerator(self):
        # unit numerator and paranthensis
        test_sets = {"1/s":{"s": -1},
                     "1/(s)":{"s": -1},
                     "(1)/s":{"s": -1}, 
                     "1/(s^2)":{"s": -2},
                     "1/s^-1":{"s": 1}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_multiple_den(self):
        # everything else, split out portions as we find issues.
        test_sets = {"m/(s/A)":{"m": 1, "s": -1, "A": 1},
                     "m/(s)/s":{"m": 1, "s": -2},
                    "m/(s/s)":{"m": 1},
                     "kg/s/A/s":{"kg": 1, "s": -2, "A":-1},
                     "m/kg/(A.s)":{"m": 1, "kg": -1, "s": -1, "A":-1}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_dots(self):
        # everything else, split out portions as we find issues.
        test_sets = {"m/(.s/A)":{"m": 1, "s": -1, "A": 1},
                     "m/(s.)/s":{"m": 1, "s": -2}}#,
#                    "m/(s/s.)":{"m": 1},
 #                    ".kg/s/A/s":{"kg": 1, "s": -2, "A":-1},
  #                   "(.kg)/A/s/A":{"kg": 1, "A": -2, "s":-1},
   #                  "m/.kg./(A.s...)":{"m": 1, "kg": -1, "s": -1, "A":-1}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

    def test_create_full(self):
        # everything else, split out portions as we find issues.
        test_sets = {"m/(s.kg^2)":{"m": 1, "s": -1, "kg": -2},
                     "m/(s)/(kg^2)":{"m": 1, "s": -1, "kg": -2},
                     "kg/(.s)":{"kg": 1, "s": -1},
                     "kg/.s":{"kg": 1, "s": -1},
                     "kg/s":{"kg": 1, "s": -1},
                     "kg/(1.s)":{"kg": 1, "s": -1}}
        for ustring, sdict in test_sets.items():
            u = Units.from_string(ustring)
            self.assertDictEqual(u.s, sdict)

class TestCase_units_maths(unittest.TestCase):
    def test_equals(self):
        test_sets = [["m","m"],
                     ["1","1"],
                     ["kg^2","kg.kg"]]
        for u1s, u2s in test_sets:
            u1 = Units.from_string(u1s)
            u2 = Units.from_string(u2s)
            self.assertTrue(u1 == u2, msg=f"{u1s} and {u2s}")

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
