import unittest

class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.units.types import DependantPhysicalQuantity
        cls.DPQ = DependantPhysicalQuantity

    def test_create(self):
        z1 = self.DPQ("")

    def test_multiply_instance(self):
        pass

    def test_multiply_scalar(self):
        pass

    def test_subtract(self):
        pass

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.units.types import logger
    logger.setLevel(logging.INFO)

    unittest.main()
