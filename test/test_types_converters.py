import unittest
from pyee.types.prefixes import Prefix

class TestCase_vp_from_number(unittest.TestCase):
    def test_basic(self):
        pass

class TestCase_vpu_from_ustring(unittest.TestCase):
    def test_basic(self):
        pass

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.converters import logger
    logger.setLevel(logging.INFO)

    unittest.main()
