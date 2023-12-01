import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as tkr
from matplotlib.lines import Line2D


plt.style.use("default")
group_thousands = tkr.FuncFormatter(lambda x, pos: "{:0,d}".format(int(x)))


_Leistung = 60  # MW
_Fixkosten = 961  # EUR / MW für 25 km Leitung
_Invest = 2135  # EUR / MW / km
_Length = range(10, 80, 11)

VoLL = 7 * [157 * _Leistung * 720 * 12 * 0.01 / 1000000]


def berechnung_der_kosten_pro_jahr(
    Leistung=None, Fixkosten=None, Invest=None, Length=None
):
    cost = []
    for schritt in Length:
        anschaffung = Leistung * Invest * schritt
        abschreibung = anschaffung / 20
        kal_zinsen = anschaffung * 0.05
        laufende = Leistung * schritt / 25 * Fixkosten
        kosten = abschreibung + kal_zinsen + laufende
        cost.append(kosten / 1000000)
    return cost


kosten = berechnung_der_kosten_pro_jahr(_Leistung, _Fixkosten, _Invest, _Length)

fig = plt.figure(figsize=(5.5, 3), constrained_layout=False)
_gs = GridSpec(1, 1, figure=fig)
ax1 = fig.add_subplot(_gs[0, 0])
ax1.plot(_Length, kosten, marker="d", color="#183A1D", markersize=0, linewidth=2.5)
ax1.plot(_Length, VoLL, color="#F0A04B", linewidth=2.5)

ax1.set_xticks([10, 20, 30, 40, 50, 60, 70, 80])
ax1.tick_params(left=False)
ax1.spines["bottom"].set_linewidth(1.1)
ax1.spines[["top", "right", "left"]].set_visible(False)
ax1.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)

ax1.set_ylabel("Yearly costs [MEUR/a]")
ax1.set_xlabel("Length of mid-pressure pipeline [km]")

_patches = []
_patches.append(Line2D([0], [0], label="Piped gas supply (refurbished; 60 MW)", color="#183A1D", linewidth=2))
_patches.append(Line2D([0], [0], label="Off-grid solution (trucking + storage)", color="#F0A04B", linewidth=2))
fig.legend(
    handles=_patches,
    loc="lower right",
    facecolor="White",
    fontsize=8,
    framealpha=0.5,
    handlelength=0.7,
    handletextpad=0.3,
    ncol=1,
    borderpad=0.75,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(0.94, 0.25),
    title='Supply options (1% utilization)'
    
)


plt.tight_layout()
fig.savefig("Illustration_Trade_Off_Auslastung.png", dpi=1000)
