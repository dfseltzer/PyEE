"""
Polynomial helpers.  Mostly wrappers on Numpy functions with some added help to make it simpler.
"""

from pyee.types.aliases import t_numeric, t_numericArray
import numpy as np

def polyadd(c1, c2):
    """
    Adds two coefficient arrays.
    """
    if len(c1) < len(c2): # pad c1
        eq_c1 = np.pad(c1, (0, len(c2)-len(c1)), mode='constant', constant_values=0)
        eq_c2 = c2
    else: # pad c2
        eq_c1 = c1
        eq_c2 = np.pad(c2, (0, len(c1)-len(c2)), mode='constant', constant_values=0)

    return eq_c1 + eq_c2

def polysub(c1, c2):
    """
    Subtracts two coefficient arrays.
    """
    if len(c1) < len(c2): # pad c1
        eq_c1 = np.pad(c1, (0, len(c2)-len(c1)), mode='constant', constant_values=0)
        eq_c2 = c2
    else: # pad c2
        eq_c1 = c1
        eq_c2 = np.pad(c2, (0, len(c1)-len(c2)), mode='constant', constant_values=0)

    return eq_c1 - eq_c2

def polyeval(c: t_numericArray, x: t_numericArray | t_numeric) -> t_numericArray | t_numeric:
    """
    Given a polynomial with ciefficients "c", evaluate at points "x"
    
    Array index into c is the exponent
    """

    x_a = np.array(x)
    partsum = np.zeros_like(x_a)
    for e, a in enumerate(c): # iter in case lots of values...
        partsum = partsum + a * np.power(x_a,e) # equiv to +=? casting works better here...
    rval = partsum.squeeze()
    return rval

def polymul(c1, c2):
    """
    Multiplies two coefficient arrays.  Like the old polymul from np, but skips all the new
    polynomial stuff
    """

    fullmul = np.zeros((len(c1)+len(c2),1))
    for e1, a in enumerate(c1):
        for e2, b in enumerate(c2):
            fullmul[e1+e2] += a*b
    
    sqmul = fullmul.squeeze()
    nzi = np.max(sqmul.nonzero())+1
    rval = sqmul[:nzi]

    return rval

def polyprint(c, var="x", float_range=(1, 100), print_zeros=False):
    """
    Prints the given coefficient array using variable var.

    Prints values of magnitude  float_range[0] <= and < float_range[1] as floats, otherwise prints in scientific notation. 
    """
    if print_zeros:
        cparts = [(f"{v:+.2f}" if float_range[0] <= abs(v) < float_range[1] else (f"{v:+.2E}" if v != 0 else "+0.0")) + f"{var}^{i}" for i, v in enumerate(c)]
    else:
        cparts = [(f"{v:+.2f}" if float_range[0] <= abs(v) < float_range[1] else (f"{v:+.2E}")) + f"{var}^{i}" for i, v in enumerate(c) if v != 0]

    cparts_spaced = [v[0]+ " " + v[1:] for v in cparts]
    return " ".join(cparts_spaced).strip("+ ").replace(f"{var}^0","").replace(f"{var}^1",var)
    