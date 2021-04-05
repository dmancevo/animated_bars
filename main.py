from datetime import datetime, date, timedelta
import argparse
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

sns.set_style("white")
sns.set_context("poster")
sns.set_palette("mako")

METRIC = "y"
DATE_COL = "date"
ELEMENT_COL = "elem"

N = 100
df = pd.concat([pd.DataFrame(dict(
    y=np.random.uniform(0,1,N).cumsum(),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) for e in ['a', 'b', 'c', 'd', 'e', 'f']])

df.sort_values([DATE_COL, METRIC], inplace=True)
min_date = df[DATE_COL].min()
n_elements = df[ELEMENT_COL].nunique()

fig = plt.figure(figsize=(20,12))
ax = plt.axes(
    xlim=(0, df[METRIC].max()),
    ylim=(0, n_elements + 1),
    position=[0,.2,.9,.9],
)
ax.axis('off')
bars = ax.barh(
    y=[i+1 for i in range(n_elements)],
    width=[1 for _ in range(n_elements)],
    color=sns.color_palette()[:n_elements],
    alpha=.7,
)
def update(i):
    d = min_date + timedelta(days=i)
    _df = df[df[DATE_COL]==d]\
        .assign(Rank = lambda x: x[METRIC].rank())
    for patch, t in zip(bars.patches, _df.iterrows()):
        _, row = t
        patch.set_width(row[METRIC])
        patch.set_y(row.Rank)
    return bars.patches
anim = FuncAnimation(fig, update, frames=100, interval=40, blit=True)
anim.save('plot.mp4', writer='ffmpeg')
