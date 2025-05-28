"""
Regular expressions used by this module for stuff...
"""

import re

# matches: 1e3 10 1.0k 0.1k etc. 
re_number_and_prefix = re.compile(r"^(?P<number>(?:[-+]?\d+\.?\d*[eE][-+]?\d+)|(?:[-+]?\d+(\.\d+)?))(?P<prefix>[a-zA-Z]?)$")
