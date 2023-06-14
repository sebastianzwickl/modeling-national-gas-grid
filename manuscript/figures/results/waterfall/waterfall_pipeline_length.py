# IMPORT MODULES
import pandas as pd
import waterfall_chart
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from waterfall_ax import WaterfallChart
import matplotlib as mpl


# PREPARE FIGURE ENVIRONMENT 
plt.rcParams.update(plt.rcParamsDefault)
plt.rc('font', family='serif', size=10, weight='medium')


# READ DATA FILES
elec_high = pd.read_excel('elec.xlsx', sheet_name='High')
elec_mid = pd.read_excel('elec.xlsx', sheet_name='Mid')
gm_high = pd.read_excel('greenmethane.xlsx', sheet_name='High')
gm_mid = pd.read_excel('greenmethane.xlsx', sheet_name='Mid')


# CREATE FIGURE ENVIRONMENT

_ylim = 3500

for name, data in [['elec', elec_high], ['gm', gm_high]]:
    fig, ax = plt.subplots(1, 1, figsize=(3.5, 3.5))
    waterfall = WaterfallChart(data["Absolute"].to_list())
    wf_ax = waterfall.plot_waterfall(ax=ax)
    ax.set_xticklabels(['2025', '2025-30', '2030-40', '2040'])
    ax.set_ylim([0, _ylim])
    ax.set_ylabel('Grid length in km')
    bars = [rect for rect in ax.get_children() if isinstance(rect, mpl.patches.Rectangle)]
    bars[0].set_color('#9BABB8')
    bars[3].set_color('#E21818')

    plt.tight_layout()
    _string = 'waterfall_' + name + '_high.pdf'
    fig.savefig(_string, format='pdf')
    
for name, data in [['elec', elec_mid], ['gm', gm_mid]]:
    fig, ax = plt.subplots(1, 1, figsize=(3.5, 3.5))
    waterfall = WaterfallChart(data["Absolute"].to_list())
    wf_ax = waterfall.plot_waterfall(ax=ax)
    ax.set_xticklabels(['2025', '2025-30', '2030-40', '2040'])
    ax.set_ylim([0, _ylim])
    ax.set_ylabel('Grid length in km')
    bars = [rect for rect in ax.get_children() if isinstance(rect, mpl.patches.Rectangle)]
    bars[0].set_color('#9BABB8')
    bars[3].set_color('#609EA2')
    plt.tight_layout()
    _string = 'waterfall_' + name + '_mid.pdf'
    fig.savefig(_string, format='pdf')