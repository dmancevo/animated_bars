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

IMAGES = [
    plt.imread("https://www.libertygames.co.uk/images/desc/Sonic-Logo(3).jpg", format='jpeg')
for _ in range(7)]

N = 400
df = pd.concat([pd.DataFrame(dict(
    y=np.random.uniform(0,10,N).cumsum(),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) for e in ['sonic','diego','sam','frodo','gendry', 'player_1', 'player_2']])

df.sort_values([DATE_COL, METRIC], inplace=True)
min_date = df[DATE_COL].min()
n_elements = df[ELEMENT_COL].nunique()

# Figure and axes.
fig = plt.figure(figsize=(20,12))
ax = fig.add_subplot( # Use this axes for the bars.
    xlim=(0, df[METRIC].head(n_elements * 100).max()),
    ylim=(0, n_elements + 2.3),
    position=[.15,.2,.9,.9],
    frame_on=False,
)
ax0 = fig.add_subplot( # Use this axes for names/logos.
    position=[0,.2,.15,.9],
    frame_on=False,
    ylim=(0, n_elements + 2.3)
)
ax1 = fig.add_subplot(position=[0,0,1,.2], frame_on=False) # Use this axes for date and theme picture.
for _ax in [ax, ax0, ax1]:
    _ax.axis('off')
# Artists.
bars = ax.barh(
    y=[0 for i in range(n_elements)],
    width=[1 for _ in range(n_elements)],
    color=sns.color_palette()[:n_elements],
    alpha=.6,
)
curr_date = ax1.text(x=0.1, y=0.5, s="", alpha=0.7, fontdict={
    "fontfamily": "sans-serif",
    "fontsize":120,
})
labels = [ax.text(
    x=0, y=0, s="", fontdict={
        "fontfamily": "sans-serif",
        "fontsize":"medium",
        "horizontalalignment": "center",
    },
) for _ in range(n_elements)]
imagebox = OffsetImage(THEME_IMAGE, zoom=0.32)
ab = AnnotationBbox(imagebox, xy=(.5, .5), xybox=(0.8, 0.7), frameon=False)
ab.set_animated(True)
ax1.add_artist(ab)
images = []
for pic in IMAGES:
    imagebox = OffsetImage(pic, zoom=0.5)
    ab = AnnotationBbox(imagebox, xy=(.5, .5), frameon=False)
    ab.set_animated(True)
    ax0.add_artist(ab)
    images.append(ab)

# Animation.
def update(i):
    d = min_date + timedelta(days=i)
    _df = df[df[DATE_COL]==d]\
        .assign(Rank = lambda x: x[METRIC].rank())
    # Adjust the x-axis to keep up with the growing numbers.
    a,b = ax.get_xlim()
    m = _df[METRIC].max()
    if 0.8 * b < m:
        ax.set_xlim(a, m/0.8)
    # Update artists.
    curr_date.set_text(f"{d.year} {d.strftime('%b')}")
    for t, patch, txt, elem in zip(_df.iterrows(), bars.patches, labels, images):
        _, row = t
        patch.set_width(row[METRIC])
        patch.set_y(row.Rank)
        txt.set_text(f"{row[METRIC]:.2f}")
        txt.set_x(row[METRIC]*1.05)
        txt.set_y(row.Rank + patch.get_height()/2.5)
        elem.xybox=(0.5, row.Rank + patch.get_height()/2.5)
    return bars.patches + labels + images + [curr_date]
anim = FuncAnimation(fig, update, frames=N, interval=40, blit=True)
anim.save('plot.mp4', writer='ffmpeg')
