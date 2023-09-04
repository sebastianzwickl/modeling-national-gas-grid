import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import geopandas


"""
    IMPORT & EXPORT POINTS
"""
_size = 15
entry_exit = {
    'Überackern': _size,
    'Arnoldstein': _size,
    'Weiden an der March': _size,
    'Neustift im Mühlkreis': _size,
    'Kittsee': _size,
    'Straß in Steiermark': _size,
    'Hörbranz' : _size,
    'Feldkirch': _size,
    'Vils' : _size,
    'Kufstein':_size
    }


"""
    DOMESTIC FOSSIL NATURAL GAS PRODUCTION
"""
nationale_produktion = {
    'Schönkirchen-Reyersdorf': '#b79ebc',
    'Stockerau': '#b79ebc',
    'Redlham': '#b79ebc',
    'Lengau': '#b79ebc'
    }


"""
    NATURAL GAS STORAGE
"""
_size2 = 10
speicher = {
    'Schönkirchen-Reyersdorf': _size2,
    'Weikendorf': _size2,
    'Gampern': _size2,
    'Straßwalchen': _size2,
    'Lengau': _size2,
    'Seekirchen am Wallersee': _size2
    }


"""
    COLORS
"""
_c_tra = '#000000'
_c_high = '#E21818'
_c_mid = '#609EA2'



"""
    FIGURE ENVIRONMENT
"""
fig = plt.figure(figsize=(6.5, 3), constrained_layout=False)
_gs = GridSpec(1, 1, figure=fig)
ax = fig.add_subplot(_gs[0, 0])


austria = gpd.read_file('at_lau/at_lau.shp')
districts = gpd.read_file('at_lau/at_lau.shp')
polygon = districts.geometry.unary_union
gdf2 = geopandas.GeoDataFrame(geometry=[polygon])
gdf2.boundary.plot(ax=ax, linewidth=0.15, color='gray')


# TRANSMISSION PIPELINES
fernleitungen = gpd.read_file('transmission/transmission.shp')
fernleitungen.drop(index=25, inplace=True)
fernleitungen.plot(ax=ax, color=_c_tra, linewidth=1.5, zorder=3)
# HIGH-PRESSURE PIPELINES
high = gpd.read_file('high/high.shp')
high.plot(ax=ax, color=_c_high, linewidth=1.25, zorder=2)
# MID-PRESSURE PIPELINES
mid = gpd.read_file('mid/mid.shp')
mid.plot(ax=ax, color=_c_mid, linewidth=1, zorder=1)


'''ENTRY EXIT'''
austria.centroid.plot(
    ax=ax, color='#023e7d',
    marker='d',
    markersize=[entry_exit.get(LAU, 0) for LAU in austria.LAU_NAME],
    zorder=4
)
'''NATIONALE PRODUKTION'''
austria.plot(
    ax=ax, 
    color=[nationale_produktion.get(LAU, 'white') for LAU in austria.LAU_NAME],
    zorder=-2)
'''NATIONALE SPEICHER'''
austria.centroid.plot(
    ax=ax, color='#8ecae6',
    marker='s',
    markersize=[speicher.get(LAU, 0) for LAU in austria.LAU_NAME],
    zorder=2
)


ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])


# GRID PRESSURE LEVELS
_patches = [mpatches.Patch(color=_c_tra, label='Transmission'),
            mpatches.Patch(color=_c_high, label='High-pressure'), mpatches.Patch(color=_c_mid, label='Mid-pressure')]


_patches1 = [Line2D(range(1), range(1), color="white", marker='d', markersize=7,
                    markerfacecolor='#023e7d', label='Entry and exit points'),
             Line2D(range(1), range(1), color="white", marker='s', markersize=6,
                    markerfacecolor='#8ecae6', label='Austrian gas storage'),
             Line2D(range(1), range(1), color="white", marker='s', markersize=6,
                    markerfacecolor='white', label=''),
             Line2D(range(1), range(1), color="white", marker='s', markersize=6,
                    markerfacecolor='#b79ebc', label='Domestic fossil natural gas generation')]

_legend = fig.legend(handles=_patches1, loc='lower left', facecolor=None, fontsize=7.5, framealpha=0.1, handlelength=0.7,
                     handletextpad=0.3, ncol=2, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=False,
                     bbox_to_anchor=(0.025, 0.02), labelspacing = 0.75
                     )

_legend.get_frame().set_linewidth(0.5)

_legend = ax.legend(handles=_patches, loc='upper left', facecolor=None, fontsize=7, framealpha=1, handlelength=0.7,
                    handletextpad=0.5, ncol=1, borderpad=0.75, columnspacing=1, edgecolor="grey", frameon=True,
                    bbox_to_anchor=(0.085, 0.9), title='Gas grid levels'
                    )
_legend.get_frame().set_linewidth(0.25)
plt.setp(_legend.get_title(),fontsize=9)


# fig.text(
#     x=1,
#     y=0.01,
#     s='Modeled gas grid: 738 pipeline sections (lines); 657 supply and demand points (nodes)',
#     ha='right',
#     fontsize=5,
#     color='#7f7f7f'
# )

plt.tight_layout()

plt.show()
# fig.savefig('Update_Austrias_existing_network.jpg', dpi=2000)
fig.savefig('2023_existing_natural_gas_grid.pdf', format='pdf')