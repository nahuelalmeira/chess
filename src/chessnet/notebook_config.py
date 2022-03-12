import pandas as pd
import igraph as ig
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

from chessnet.utils import ARTIFACTS_DIR, DATA_DIR, FIGS_DIR, Database
from chessnet.mpl_settings_v3 import *

database_latex = {"OTB": r"$\mathrm{OTB}$", "Portal": r"$\mathrm{Portal}$"}
