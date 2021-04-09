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

METRIC = "y"
ORDER_COL = "date"
NAME_COL = "elem"
N = 200
df = pd.concat([pd.DataFrame(dict(
    y=np.clip(5+np.random.normal(i*1e-1,1,N).cumsum(), 1, None),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) \
        for i, e in enumerate(['sonic','diego','sam','frodo','gendry','p1','p2','p3','p4','p5'])])


df.sort_values([ORDER_COL, METRIC], inplace=True)
TIMEFRAMES = df[ORDER_COL].unique()
ELEMENTS = df[NAME_COL].unique()

def update(i):
    _df = df[df[ORDER_COL] == TIMEFRAMES[i]]
    plt.cla()
    bars = plt.barh(_df[NAME_COL], _df[METRIC], color=PALETTE[:_df.shape[0]])
    plt.title("Test Title")
    plt.suptitle("Test Sup-Title")
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tick_params(left=False, bottom=False, labelbottom=False)
    for bar in bars:
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height()/2,
            f"  {bar.get_width():.0f}", va='center'
        )

fig = plt.figure(figsize=[20,12])
anim = FuncAnimation(fig, update, interval=100, frames=len(TIMEFRAMES), repeat=False)
anim.save('mov.mp4', writer='ffmpeg')
