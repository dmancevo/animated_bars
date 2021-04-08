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
from numba import njit
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
                                       "images/desc/Sonic-Logo(3).jpg"), format="jpeg") for _ in range(10)]

# Data-set.
METRIC = "y"
DATE_COL = "date"
NAME_COL = "elem"
N = 200
df = pd.concat([pd.DataFrame(dict(
    y=np.clip(5+np.random.normal(i*1e-1,1,N).cumsum(), 1, None),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) \
        for i, e in enumerate(['sonic','diego','sam','frodo','gendry','p1','p2','p3','p4','p5'])])

df['y'] = df.y.rolling(14).mean()
df.dropna(inplace=True)

df.sort_values([DATE_COL, METRIC], inplace=True)
MIN_DATE = df[DATE_COL].min()
N_ELEMENTS = df[NAME_COL].nunique()

MAX_ELEMENTS = 7


# Figure and axes.
FIG = plt.figure(figsize=(20,12))
MAIN_AX = FIG.add_subplot( # Use this axes for the bars.
    xlim=(0, df[METRIC].head(N_ELEMENTS * 100).max()),
    ylim=(0, MAX_ELEMENTS + 2.3),
    position=[.15,.2,.9,.9],
    frame_on=False,
)
LEFT_AX = FIG.add_subplot( # Use this axes for names/logos.
    position=[0,.2,.15,.9],
    frame_on=False,
    ylim=(0, MAX_ELEMENTS + 2.3)
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
#ID_ART = [add_image(LEFT_AX, img, zoom=0.5, xybox=(0, 0)) \
            #for img in ELEMENT_IMAGE_LOCATIONS]
ID_ART = [LEFT_AX.text(x=0, y=0, s=name, fontdict={"fontfamily": "sans-serif", "fontsize":36}) \
                for name in df[NAME_COL].unique()]

# Elements.
Element = namedtuple('Element', ['name', 'bar_art', 'bar_color', 'number_art', 'id_art'])
ELEMENTS = {}
for i, name, bar_art, number_art, id_art \
    in zip(range(N_ELEMENTS), df[NAME_COL].unique(), BARS_ART.patches, NUMBERS_ART, ID_ART):
    ELEMENTS[name] = Element(
        name=name,
        bar_art=bar_art,
        bar_color=PALETTE[i % len(PALETTE)],
        number_art=number_art,
        id_art=id_art
    )

# Animation.
@njit
def get_rank(
    rank: float,
    m: float,
    m_below: float,
    m_above: float,
    per:float=.20,
    max_elements:int=MAX_ELEMENTS,
    ) -> float:
    rank = rank - (N_ELEMENTS - MAX_ELEMENTS)
    if ( np.isnan(m_above) and (1-per) < (m_below/m) ) \
        or ( (m_below/m) >= (m/m_above) and (1-per) < (m_below/m) ):
        alpha = np.round((m_below - (1-per)*m) / (per*m), 2)
        return (1-alpha) * rank + alpha * (rank-1)
    elif ( np.isnan(m_below) and (1-per) < (m/m_above) ) \
        or ( (m_below/m) < (m/m_above) and (1-per)*m_above < (m/m_above) ):
        alpha = np.round((m - (1-per)*m_above) / (per*m_above), 2)
        return (1-alpha) * (rank+1) + alpha * rank
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
        if rank < .9: rank = -20 # Move out of the plot.
        elem.bar_art.set_width(row[METRIC])
        elem.bar_art.set_y(rank)
        elem.number_art.set_text(f"{row[METRIC]:.2f}")
        elem.number_art.set_x(row[METRIC]*1.07)
        elem.number_art.set_y(rank + elem.bar_art.get_height()/2.5)
        id_pos = (0.5, rank + elem.bar_art.get_height()/2.5 if rank > 0 else -20)
        if hasattr(elem.id_art, 'xybox'):
            elem.id_art.xybox=id_pos
        else:
            elem.id_art.set_position(xy=id_pos)
        updated_artists += [elem.bar_art, elem.number_art, elem.id_art]
    return updated_artists

anim = FuncAnimation(FIG, update, frames=N, interval=100, blit=True)
anim.save('mov.mp4', writer='ffmpeg')
