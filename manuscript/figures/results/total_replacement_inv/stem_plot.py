import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_excel('2040_Methan_Investitionen.xlsx')
scenarios = data.loc[0][1::].to_list()
scenarios[1] = 'Elec'
values = data.loc[4][1::].to_list()

df = pd.DataFrame(data={
    'Scenario' : scenarios,
    'Total repl. inv. in MEUR' : values
    })

df.sort_values('Total repl. inv. in MEUR', inplace=True, ascending=True)

plt.rcParams.update(plt.rcParamsDefault)
plt.rc('font', family='serif', size=10, weight='medium')

fig, ax = plt.subplots(1, 1, figsize=(5, 2))
ax.stem([0, 1, 2, 3], values, orientation='horizontal', linefmt = '--', basefmt = 'k:')
plt.tight_layout()
fig.savefig('investments2040.pdf', format='pdf')

fig, ax = plt.subplots(1, 1, figsize=(5, 2))
ax.barh(df.Scenario, df['Total repl. inv. in MEUR'], align='center', 
        color='#DEDEA7', edgecolor = 'black', linewidth=0.25)

for i, v in enumerate(df['Total repl. inv. in MEUR']):
    ax.text(v - 143/2, i, str(v), color='black', va='center', ha='center')

ax.set_xlim([0, 200])

ax.tick_params(left=False)
ax.spines["bottom"].set_linewidth(1.1)
ax.spines[["top", "right", "left"]].set_visible(False)
# ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
ax.set_xlabel('Total replacement investments in MEUR')
plt.tight_layout()
fig.savefig('replace_inv_2040.pdf', format='pdf')


# fig.tight_layout(pad=4)
# plt.subplot(1,2,1)
# plot_hor_bar_2()
# top_sorted = top10_spirit.sort_values('spirit_servings',
#                                       ascending=True)\
#                          .set_index('country')
# plt.subplot(1,2,2)
# plt.hlines(y=top_sorted.index, xmin=0, xmax=top_sorted,
#            color='slateblue')
# plt.plot(top_sorted, top_sorted.index,
#          'o', color='slateblue')
# plt.title('TOP10 countries by spirit consumption', fontsize=28)
# plt.xlabel('Servings per person', fontsize=23)
# plt.xticks(fontsize=20)
# plt.xlim(0, None)
# plt.ylabel(None)
# plt.yticks(fontsize=20)
# sns.despine(left=True)
# ax.grid(False)
# ax.tick_params(bottom=True, left=False)
# plt.show()