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
sns.set_palette("mako")


df = pd.read_csv("API_NY/API_NY.GDP.PCAP.KD_DS2_en_csv_v2_2163576.csv", skiprows=4)


def get_bars(df:pd.DataFrame) -> list[tuple[list[str], list[float]]]:
    bars = []
    curr_date = date(1960,1,1)
    while curr_date <= date(2019, 1, 1):
        if curr_date.month == 1 and curr_date.day== 1:
            year = f"{curr_date.year}"
            next_year = f"{curr_date.year + 1}"
            countries = (
                df[['Country Name', year]]
                .groupby('Country Name')
                .max().dropna()
                .sort_values(year, ascending=False)
                .join(
                    df[['Country Name', next_year]]\
                    .set_index("Country Name"), how="left"
                )
                .reset_index()
            )
        alpha = (curr_date - date(curr_date.year, 1, 1)).days / 365
        countries['GDP Percapita'] = (1-alpha) * countries[year] + alpha * countries[next_year]
        bars.append((countries['Country Name'].head(20).tolist(),
                     countries['GDP Percapita'].head(20).tolist()))
        curr_date += timedelta(days=1)
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
    bar_artists: matplotlib.container.Container,
) -> Callable[[int], list[matplotlib.artist.Artist]]:
    
    colors = {}
    
    def update(i:int)->list[matplotlib.artist.Artist]:
        nonlocal bars, bar_artists, colors
        countries, values = bars[i]
        for country, value, bar in zip(countries, values, bar_artists.patches):
            bar.set_width(value)
#             bar.set_y(country)
        return bar_artists.patches
    
    return update


def make_anim(bars:list[tuple[list[str],list[float]]], file_name:str="mov.mp4", **kwargs):
    palette = sns.color_palette()
    fig = plt.figure(figsize=[20,12])
    ax = plt.gca()
    bar_artists=ax.barh(['' for _ in range(10)], [0 for _ in range(10)])
    anim = FuncAnimation(fig,
        get_update(bars, bar_artists),
        interval=200, frames=len(bars), repeat=False, blit=True,
    )
    anim.save(file_name, writer='ffmpeg')
    
make_anim(get_bars(df)[:100])