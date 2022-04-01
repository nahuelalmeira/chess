import string
import pickle
from IPython.display import display

import pandas as pd
import igraph as ig
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics import normalized_mutual_info_score

from chessnet.utils import ARTIFACTS_DIR, DATA_DIR, FIGS_DIR, Database
from chessnet.mpl_settings_v3 import *
from chessnet.graphs import (
    read_pickle,
    read_rewired_graph,
    read_randomized_edgelist,
    read_gml,
)
from chessnet.auxiliary import linear_regression, powerlaw

database_latex = {"OTB": r"$\mathrm{OTB}$", "Portal": r"$\mathrm{Portal}$"}

panels = [r"$\mathbf{(" + c + r")}$" for c in string.ascii_lowercase]
