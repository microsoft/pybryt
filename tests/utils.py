""""""

import numpy as np
import pandas as pd


class AttrDict(dict):

    def __getattr__(self, attr):
        return self[attr]
