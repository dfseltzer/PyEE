"""
Basic math functions - probably could be split out in the future.
"""
import numpy as np

def rms_error(a, b):
    """
    RMS error between two numbers or 1 x N arrays.  nan values are treated as zero
    """
    try:
        len(a)
    except TypeError as _:
        try:
            len(b)
        except TypeError as _: # both are singles
            return np.abs(a-b)
        return np.sqrt(np.sum(np.square(a-b))/len(b)) # a is single, b is array - use b length
    
    try:
        len(b)
    except: 
        return np.sqrt(np.nansum(np.square(a-b))/len(a)) # b is single, a is array - use a length

    if len(a) != len(b):
        raise ValueError(f"Inputs have unequal lengths > 1... len(a) = {len(a)} != len(b) = {len(b)}")

    return np.sqrt(np.nansum(np.square(a-b))/len(a)) # both are arrays - just use a