import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
import pyam
import matplotlib.ticker as tkr
from matplotlib.lines import Line2D


group_thousands = tkr.FuncFormatter(lambda x, pos: '{:0,d}'.format(int(x)))
plt.rcParams.update(plt.rcParamsDefault)

fig = plt.figure(figsize=(4, 4), constrained_layout=False)
_gs = GridSpec(2, 2, figure=fig)
ax1 = fig.add_subplot(_gs[0, 0])
ax2 = fig.add_subplot(_gs[0, 1])
ax3 = fig.add_subplot(_gs[1, 0])
ax4 = fig.add_subplot(_gs[1, 1])

fig.suptitle("Demand of natural gas and hydrogen by 2040")

ax1.set_title("Elec", fontsize=10, y=0.825, loc='center')
ax2.set_title("GG", fontsize=10, y=0.825, loc='center')
ax3.set_title("DGG", fontsize=10, y=0.825, loc='center')
ax4.set_title("GM", fontsize=10, y=0.825, loc='center')

bar_width = 4
h2_color = '#B5C99A'
gas_color = '#862B0D'

"""
    ELECTRIFICATION
"""
years = [2030, 2040]
gas = [50.2, 7.3]
hydrogen = [4.7, 29.8]
ax1.bar(years, gas, width=bar_width, color=gas_color)
ax1.bar(years, hydrogen, bottom=gas, color=h2_color, width=bar_width)
ax1.set_xlim([2025, 2045])
ax1.set_ylim([0, 110])


"""
    GREEN GASES
"""
y1 = [60.8, 9.6]
y2 = [13.5, 86.0]
ax2.bar(years, y1, color=gas_color, width=bar_width)
ax2.bar(years, y2, bottom=y1, color=h2_color, width=bar_width)
ax2.set_ylim([0, 110])


"""
    DECENTRALIZED GREEN GASES
"""
y1 = [63.9, 20.4]
y2 = [20.4, 84.1] 
ax3.bar(years, y1, color=gas_color, width=bar_width)
ax3.bar(years, y2, bottom=y1, color=h2_color, width=bar_width)
ax3.set_ylim([0, 110])


"""
    GREEN METHANE
"""
y1 = [80, 84.8]
y2 = [1.7, 12.8] 
ax4.bar(years, y1, color=gas_color, width=bar_width)
ax4.bar(years, y2, bottom=y1, color=h2_color, width=bar_width)


"""
    LEGEND
"""
_patches = [
    Line2D(range(1), range(1), color=gas_color, label='Natural gas', linewidth=1.5),
    Line2D(range(1), range(1), color=h2_color, label='Hydrogen', linewidth=1.5),
]
plt.tight_layout()
_legend = ax1.legend(handles=_patches, 
                     loc='center', 
                     facecolor=None, 
                     fontsize=9, 
                     framealpha=1, 
                     handlelength=0.7,
                     handletextpad=0.5, 
                     ncol=2, 
                     borderpad=0.5, 
                     columnspacing=1, 
                     edgecolor="grey", 
                     frameon=False, 
                     bbox_to_anchor=(1.1, 1.085)
                     )

_legend.get_frame().set_linewidth(0.25)








fig.savefig("Demand.pdf", format="pdf")