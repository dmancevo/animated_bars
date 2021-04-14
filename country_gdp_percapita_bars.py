from typing import Callable
import argparse
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage
from matplotlib.offsetbox import AnnotationBbox
import seaborn as sns
import ssl
from subprocess import run

ssl._create_default_https_context = ssl._create_unverified_context

sns.set_style("white")
sns.set_context("poster")
sns.set_palette("rocket")


df = pd.read_csv("API_NY/API_NY.GDP.PCAP.KD_DS2_en_csv_v2_2163576.csv", skiprows=4)


def get_bars(df:pd.DataFrame, start_year=1960, end_year=2019) -> list[tuple[list[str], list[float]]]:
    bars = []
    cols = set(df.columns)
    for year in range(start_year, end_year):
        while 1:
            next_year = year + 1
            if f"{next_year}" in cols:
                break
        df[f"{year+1}"].fillna(df[f"{year}"], inplace=True)
        for alpha in np.arange(0,1.05,.05):
            df['GDP Percapita'] = (1-alpha) * df[f"{year}"] + alpha * df[f"{year+1}"]
            df.sort_values('GDP Percapita', ascending=False, inplace=True)
            bars.append((year if alpha < 1 else year+1,
                         df['Country Name'].head(20).tolist(),
                         df['GDP Percapita'].head(20).tolist()))
    return bars


def add_image(
        ax:matplotlib.axes.Axes,
        ticker:str, zoom:float, xybox:tuple[float,float]
    ) -> matplotlib.offsetbox.AnnotationBbox:
    try:
        image = plt.imread(f"ticker_images/{ticker}.png")
    except FileNotFoundError:
        return None
    imagebox = OffsetImage(image, zoom=zoom)
    ab = AnnotationBbox(imagebox, xy=(.5,.5), xybox=xybox, frameon=False)
    ab.set_animated(True)
    ax.add_artist(ab)
    return ab


def get_update(
    bars:list[tuple[list[str],list[float]]],
    )->Callable[[int], None]:
    colors = {}
    palette = sns.color_palette()
    def update(i:int)->None:
        nonlocal bars, colors, palette
        year, countries, values = bars[i]
        plt.cla()
        col = []
        for c in countries:
            if c not in colors:
                colors[c] = palette[np.random.choice(len(palette))]
            col.append(colors[c])
        barC = plt.barh(np.arange(len(countries), 0, -1), values, tick_label=countries, color=col)
        plt.title(f"Year: {year}", fontsize=50)
        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_visible(False)
        for l in ax.get_yticklabels():
            l.set_fontsize(20)
        plt.tick_params(left=False, bottom=False, labelbottom=False)
        width=max([bar.get_width() for bar in barC])
        for bar in barC:
            ax.text(
                bar.get_width(),
                bar.get_y() + .2 * bar.get_height(),
                f"  ${bar.get_width():.0f}", va='center',
                fontsize=20,
            )
    return update


def make_anim(bars:list[tuple[list[str],list[float]]], file_name:str="mov.mp4", **kwargs):
    palette = sns.color_palette()
    fig = plt.figure(figsize=[25,12])
    anim = FuncAnimation(fig,
        get_update(bars),
        interval=100, frames=len(bars), repeat=False,
    )
    anim.save(file_name, writer='ffmpeg')
    
make_anim(get_bars(df, 1960, 2018))
