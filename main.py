from datetime import datetime, date, timedelta
import argparse
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
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

THEME_IMAGE = plt.imread("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/1280px-Olympic_rings_without_rims.svg.png", format="png")

N = 400
df = pd.concat([pd.DataFrame(dict(
    y=np.random.uniform(0,10,N).cumsum(),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) for e in ['a','b','c','d','e']])

df.sort_values([DATE_COL, METRIC], inplace=True)
min_date = df[DATE_COL].min()
n_elements = df[ELEMENT_COL].nunique()

IMAGES = [
    plt.imread("https://www.libertygames.co.uk/images/desc/Sonic-Logo(3).jpg", format='jpeg')
for _ in range(n_elements)]

fig = plt.figure(figsize=(20,12))
ax = plt.axes(
    xlim=(0, df[METRIC].max()),
    ylim=(0, n_elements + 2.3),
    position=[0,.2,.9,.9],
)
ax.axis('off')
bars = ax.barh(
    y=[0 for i in range(n_elements)],
    width=[1 for _ in range(n_elements)],
    color=sns.color_palette()[:n_elements],
    alpha=.7,
)
curr_date = ax.text(x=0.5, y=0.07, s="", alpha=0.7, fontdict={
    "fontfamily": "sans-serif",
    "fontsize":90,
})
labels = [ax.text(
    x=0, y=0, s="0", fontdict={
        "fontfamily": "sans-serif",
        "fontsize":"medium",
        "horizontalalignment": "center",
    },
) for _ in range(n_elements)]
imagebox = OffsetImage(THEME_IMAGE, zoom=0.37)
ab = AnnotationBbox(imagebox, (.5, .5), xybox=(df[METRIC].max()*0.9, 0.01), frameon=False)
ab.set_animated(True)
ax.add_artist(ab)
images = []
for pic in IMAGES:
    imagebox = OffsetImage(pic, zoom=0.5)
    ab = AnnotationBbox(imagebox, (.5, .5), frameon=False)
    ab.set_animated(True)
    ax.add_artist(ab)
    images.append(ab)
def update(i):
    d = min_date + timedelta(days=i)
    _df = df[df[DATE_COL]==d]\
        .assign(Rank = lambda x: x[METRIC].rank())
    curr_date.set_text(f"{d.year} {d.strftime('%b')}")
    for t, patch, txt, ab in zip(_df.iterrows(), bars.patches, labels, images):
        _, row = t
        patch.set_width(row[METRIC])
        patch.set_y(row.Rank)
        txt.set_text(f"{row[METRIC]:.2f}")
        txt.set_x(row[METRIC])
        txt.set_y(row.Rank)
        ab.xybox=(row[METRIC]+2, row.Rank+.5)
    return bars.patches + labels + images + [curr_date]
anim = FuncAnimation(fig, update, frames=N, interval=40, blit=True)
anim.save('plot.mp4', writer='ffmpeg')
