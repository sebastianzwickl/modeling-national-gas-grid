import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
import pyam
import matplotlib.ticker as tkr
import matplotlib.patches as mpatches

color = "gray"

group_thousands = tkr.FuncFormatter(lambda x, pos: "{:0,d}".format(int(x)))
plt.rcParams.update(plt.rcParamsDefault)
plt.rc("font", family="serif", size=10, weight="medium")

fig = plt.figure(figsize=(5, 2.5), constrained_layout=False)
_gs = GridSpec(1, 1, figure=fig)
ax1 = fig.add_subplot(_gs[0, 0])

ax1.set_ylabel("Grid costs in EUR/MWh")
_x = [2030, 2035, 2040, 2045]

ax1.spines[["top", "right", "left"]].set_visible(False)
ax1.grid(which="major", axis="y", color="#758D99", alpha=0.25, zorder=1)
ax1.tick_params(left=False)
ax1.spines["left"].set_linewidth(1.1)
ax1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])

ax1.set_xlabel("Gas demand supplied by the grid in TWh")

netzentgelte = list(
    pd.read_excel("Netzentgelte.xlsx", sheet_name="New").iloc[4].values[1:]
)
verbrauch = list(
    pd.read_excel("Netzentgelte.xlsx", sheet_name="New").iloc[3].values[1:]
)


ax1.plot(
    verbrauch[0:3],
    netzentgelte[0:3],
    color=color,
    zorder=2,
    linewidth=2,
    marker="d",
    markersize=8,
    markeredgewidth=0.25,
    markeredgecolor="black",
)
ax1.plot(verbrauch[0:3], netzentgelte[0:3], color="black", zorder=-1, linewidth=2.5)

ax1.plot(
    verbrauch[2:4],
    netzentgelte[2:4],
    color=color,
    zorder=2,
    linewidth=2,
    marker="d",
    markersize=8,
    markeredgewidth=0.25,
    markeredgecolor="black",
)
ax1.plot(
    verbrauch[2:4],
    netzentgelte[2:4],
    color="black",
    zorder=-1,
    linewidth=2.5,
    linestyle="solid",
)


ax1.text(
    verbrauch[0] + 2.5,
    netzentgelte[0],
    str("Elec"),
    ha="left",
    fontsize=10,
    color="black",
)
ax1.text(
    verbrauch[1] + 2.5,
    netzentgelte[1],
    str("GG"),
    ha="left",
    fontsize=10,
    color="black",
)
ax1.text(
    verbrauch[2] + 2.5,
    netzentgelte[2] + 0.4,
    str("DGG"),
    ha="left",
    fontsize=10,
    color="black",
)
ax1.text(
    verbrauch[3],
    netzentgelte[3] + 0.6,
    str("GM"),
    ha="center",
    fontsize=10,
    color="black",
)
ax1.set_ylim([0, 8])
plt.tight_layout()
fig.savefig("grid_charges.pdf", format="pdf")
