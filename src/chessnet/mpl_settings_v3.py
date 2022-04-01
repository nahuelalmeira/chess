import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # type: ignore
from cycler import cycler  # type: ignore

mpl.rcParams["axes.prop_cycle"] = cycler(color=sns.color_palette("deep"))

rc_font_size = 30
rc_label_size = 28
rc_legend_size = 26
mpl.rcParams["figure.figsize"] = (12, 8)
mpl.rcParams["text.usetex"] = True
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = "Computer Modern"
mpl.rcParams["lines.linewidth"] = 3
mpl.rcParams["legend.fontsize"] = rc_legend_size
mpl.rcParams["savefig.transparent"] = True
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["axes.linewidth"] = 3
mpl.rcParams["axes.labelsize"] = rc_font_size
mpl.rcParams["xtick.labelsize"] = rc_label_size
mpl.rcParams["ytick.labelsize"] = rc_label_size
mpl.rcParams["xtick.major.width"] = 3
mpl.rcParams["xtick.minor.visible"] = True
mpl.rcParams["xtick.minor.width"] = 2
mpl.rcParams["ytick.major.width"] = 3
mpl.rcParams["ytick.minor.visible"] = True
mpl.rcParams["ytick.minor.width"] = 2
mpl.rcParams["patch.linewidth"] = 1.5
mpl.rcParams["figure.titlesize"] = 24

plt.rc("text.latex", preamble=r"\usepackage{amsmath}")
