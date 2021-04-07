from datetime import datetime, date, timedelta
import argparse
from collections import namedtuple
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

PALETTE = sns.color_palette()

THEME_IMAGE = plt.imread(("https://upload.wikimedia.org/wikipedia/"
                          "commons/thumb/5/5c/Olympic_rings_without_rims.svg/"
                          "1280px-Olympic_rings_without_rims.svg.png"), format="png")

ELEMENT_IMAGE_LOCATIONS = [plt.imread(("https://www.libertygames.co.uk/"
                                       "images/desc/Sonic-Logo(3).jpg"), format="jpeg") for _ in range(7)]

# Data-set.
METRIC = "y"
DATE_COL = "date"
NAME_COL = "elem"
N = 100
df = pd.concat([pd.DataFrame(dict(
    y=np.random.uniform(0,10,N).cumsum(),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) for e in ['sonic','diego','sam','frodo','gendry', 'player_1', 'player_2']])

df.sort_values([DATE_COL, METRIC], inplace=True)
MIN_DATE = df[DATE_COL].min()
N_ELEMENTS = df[NAME_COL].nunique()


# Figure and axes.
FIG = plt.figure(figsize=(20,12))
MAIN_AX = FIG.add_subplot( # Use this axes for the bars.
    xlim=(0, df[METRIC].head(N_ELEMENTS * 100).max()),
    ylim=(0, N_ELEMENTS + 2.3),
    position=[.15,.2,.9,.9],
    frame_on=False,
)
LEFT_AX = FIG.add_subplot( # Use this axes for names/logos.
    position=[0,.2,.15,.9],
    frame_on=False,
    ylim=(0, N_ELEMENTS + 2.3)
)
BOTTOM_AX = FIG.add_subplot( # Use this axes for date and theme picture.
    position=[0,0,1,.2],
    frame_on=False
)
for _ax in [MAIN_AX, LEFT_AX, BOTTOM_AX]:
    _ax.axis('off')


# Artists.
def add_image(ax, image, zoom, xybox):
    imagebox = OffsetImage(image, zoom=0.5)
    ab = AnnotationBbox(imagebox, xy=(.5, .5), xybox=xybox, frameon=False)
    ab.set_animated(True)
    ax.add_artist(ab)
    return ab
BARS_ART = MAIN_AX.barh(
    y=[0 for i in range(N_ELEMENTS)],
    width=[1 for _ in range(N_ELEMENTS)],
    color=PALETTE[:N_ELEMENTS],
    alpha=.6,
)
DATE_ART = BOTTOM_AX.text(x=0.1, y=0.5, s="", alpha=0.7, fontdict={
    "fontfamily": "sans-serif",
    "fontsize":120,
})
NUMBERS_ART = [MAIN_AX.text(
    x=0, y=0, s="", fontdict={
        "fontfamily": "sans-serif",
        "fontsize":"medium",
        "horizontalalignment": "center",
    },
) for _ in range(N_ELEMENTS)]
THEME_ART = add_image(BOTTOM_AX, THEME_IMAGE, zoom=0.32, xybox=(0.8, 0.7))
IMAGE_ART = [add_image(LEFT_AX, img, zoom=0.5, xybox=(0, 0)) \
            for img in ELEMENT_IMAGE_LOCATIONS]

# Elements.
Element = namedtuple('Element', ['name', 'bar_art', 'bar_color', 'number_art', 'image_art'])
ELEMENTS = {}
for i, name, bar_art, number_art, image_art \
    in zip(range(N_ELEMENTS), df[NAME_COL].unique(), BARS_ART.patches, NUMBERS_ART, IMAGE_ART):
    ELEMENTS[name] = Element(
        name=name,
        bar_art=bar_art,
        bar_color=PALETTE[i % len(PALETTE)],
        number_art=number_art,
        image_art=image_art
    )

# Animation.
def get_rank(rank, m, m_below, m_above, per=.1):
    if np.isnan(m_above) and (1-per) < (m_below/m):
        alpha = (m_below - (1-per)*m) / (per*m)
        return (1-alpha) * rank + alpha * (rank-1)
    else:
        return rank


def update(i):
    curr_date = MIN_DATE + timedelta(days=i)
    _df = df[df[DATE_COL]==curr_date]\
            .assign(Rank = lambda x: x[METRIC].rank()) 
    _df['m_below'] = _df.y.shift(1)
    _df['m_above'] = _df.y.shift(-1)
    # Adjust the x-axis to keep up with the growing numbers.
    a,b = MAIN_AX.get_xlim()
    m = _df[METRIC].max()
    if 0.8 * b < m:
        MAIN_AX.set_xlim(a, m/0.8)
    # Update artists.
    updated_artists = [DATE_ART]
    DATE_ART.set_text(f"{curr_date.year} {curr_date.strftime('%b')}")
    for _, row in _df.iterrows():
        name = row[NAME_COL]
        elem = ELEMENTS[name]
        rank = get_rank(row.Rank, row[METRIC], row.m_below, row.m_above)
        elem.bar_art.set_width(row[METRIC])
        elem.bar_art.set_y(rank)
        elem.number_art.set_text(f"{row[METRIC]:.2f}")
        elem.number_art.set_x(row[METRIC]*1.05)
        elem.number_art.set_y(rank + elem.bar_art.get_height()/2.5)
        elem.image_art.xybox=(0.5, rank + elem.bar_art.get_height()/2.5)
        updated_artists += [elem.bar_art, elem.number_art, elem.image_art]
    return updated_artists

anim = FuncAnimation(FIG, update, frames=N, interval=40, blit=True)
anim.save('mov.mp4', writer='ffmpeg')
