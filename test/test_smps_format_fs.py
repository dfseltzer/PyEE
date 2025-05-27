from pyee.smps.smps import format_fs
import unittest



class TestCase_format_fs(unittest.TestCase):

    def test_create_no_default(self):
        fs1 = format_fs(inputobj="1000 Hz", defaultunits=None, inputunits=None)
        fs2 = format_fs(inputobj="1k Hz", defaultunits=None, inputunits=None)
        fs3 = format_fs(inputobj=1000, defaultunits=None, inputunits="Hz")
        fs4 = format_fs(inputobj="1k", defaultunits=None, inputunits="Hz")

        self.assertEqual(fs1, fs2)
        self.assertEqual(fs2, fs3)
        self.assertEqual(fs3, fs4)


if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
