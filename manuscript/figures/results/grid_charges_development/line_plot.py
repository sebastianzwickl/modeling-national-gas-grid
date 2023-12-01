import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.lines import Line2D

plt.rcParams.update(plt.rcParamsDefault)
plt.rc('font', family='serif', size=10, weight='medium')

fig, ax = plt.subplots(1, 1, figsize=(3, 3))

elec = [7.0, 5.2]
gg = [5.5, 4.1]
dgg = [2.7, 2.0]
gm = [1.3, 1.1]

x = [0, 1]

for elec, color, line_st in [[elec, 'gray', 'dotted'], [gg, 'gray', 'dashdot'], [dgg, 'gray', 'dashed'], [gm, 'gray', 'solid']]:
    
    ax.plot(x, elec, 
            marker='d', 
            color=color, 
            markersize=8,
            markeredgewidth=0.25,
            markeredgecolor="gray",
            linestyle=line_st
            )
    # ax.plot(x, elec, 
    #         marker='d', 
    #         color='black', 
    #         linewidth=1.75,
    #         zorder=-1, 
    #         linestyle=line_style
    #         )
    ax.text(
            0.55, 
            elec[1] + (elec[0] - elec[1]) / 2 + 0.35,
            str(np.around(elec[1] - elec[0], 1)) +r'$~\frac{EUR}{MWh}$' ,
            ha="center",
            fontsize=9,
            color=color,
    )
    


ax.set_xlim([-0.25, 1.25])
ax.set_ylim([0, 8])
ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])

ax.set_xticks([0, 1])
ax.set_xticklabels(['75 yrs.', '90-100 yrs.'])
ax.set_xlabel('Technical lifetime of pipelines')

ax.spines[["top", "right", "left"]].set_visible(False)
ax.grid(which="major", axis="y", color="#758D99", alpha=0.25, zorder=1)
ax.tick_params(left=False)
ax.spines["left"].set_linewidth(1.1)
ax.set_ylabel('Grid costs in EUR/MWh')

_patches = [
Line2D(range(1), range(1), color='gray', label='Elec', linewidth=1.5, linestyle='dotted'),
Line2D(range(1), range(1), color='gray', label='GG', linewidth=1.5, linestyle='dashdot'),
Line2D(range(1), range(1), color='gray', label='DGG', linewidth=1.5, linestyle='dashed'),
Line2D(range(1), range(1), color='gray', label='GM', linewidth=1.5),
]
_legend = ax.legend(handles=_patches, loc='upper right', facecolor=None, fontsize=8, framealpha=1, handlelength=1.75,
                handletextpad=0.5, ncol=4, borderpad=0.35, columnspacing=1, edgecolor="grey", frameon=True, bbox_to_anchor=(1.05, 1.05))
_legend.get_frame().set_linewidth(0.25)
plt.tight_layout()

fig.savefig('cleaned_grid_charges.pdf', format='pdf')
