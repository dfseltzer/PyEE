"""
Helper functions to tie it all together
"""

import json
import os
import pathlib

DATA_REL_PATH = r".\data"
DATA_ABS_PATH = None

if DATA_ABS_PATH is None:
    fpath, fname = os.path.split(__file__)
    DATA_ABS_PATH = pathlib.Path(fpath, DATA_REL_PATH)


def load_data_file(fname):
    """
    Load a data file from the data directory.

    :param fname: filename to load. not including suffix or path.
    :return: data loaded from file as dict
    """

    full_path = pathlib.Path(DATA_ABS_PATH, fname+".json")

    with open(full_path,"r") as fobj:
        fdat = json.load(fobj)

    return fdat

