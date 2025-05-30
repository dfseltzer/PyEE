"""
Regular expressions used by this module for stuff...
"""

import re

# matches: 1e3 10 1.0k 0.1k etc.  Creates match group for number and prefix.
re_number_and_prefix = re.compile(r"^(?P<number>(?:[-+]?\d+\.?\d*[eE][-+]?\d+)|(?:[-+]?\d+(\.\d+)?))(?P<prefix>[a-zA-Z]?)$")

# matches: /(a^b), /(a), /(a.b^c), etc.  For matching grouped denominators in unit strings
re_ustring_den_group = re.compile(r"/\(([a-zA-Z]+(?:\^[+-]?\d+)?|1)?(?:\.+[a-zA-Z]+(?:\^[+-]?\d+)?)*\)")

# matches: single denominators with any number of . in front such as /..s, /a^b, etc.
re_ustring_single_den = re.compile(r"/\.*(?P<u>[a-zA-Z]+)(?P<e>\^[+-]?\d+)?\.*")

# matches: unit string elements without an exponent
re_ustring_non_exp_sets = re.compile(r"(?:[a-zA-Z]+(?=\.))|(?:[a-zA-Z]+$)")
