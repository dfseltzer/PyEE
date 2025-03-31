"""
Polynomial helpers
"""

import numpy

def polyeval(c, x):
    """
    Given a polynomial with ciefficients "c", evaluate at points "x"
    
    Array index into c is the exponent
    """

    x_a = numpy.array(x)
    partsum = numpy.zeros_like(x_a)
    for e, a in enumerate(c): # iter in case lots of values...
        partsum = partsum + a * numpy.power(x_a,e) # equiv to +=? casting works better here...
    rval = partsum.squeeze()
    return rval

def polymul(c1, c2):
    """
    Multiplies two coefficient arrays.  Like the old polymul from numpy, but skips all the new
    polynomial stuff
    """

    fullmul = numpy.zeros((len(c1)+len(c2),1))
    for e1, a in enumerate(c1):
        for e2, b in enumerate(c2):
            fullmul[e1+e2] += a*b
    
    sqmul = fullmul.squeeze()
    nzi = numpy.max(sqmul.nonzero())+1
    rval = sqmul[:nzi]

    return rval