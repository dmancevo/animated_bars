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
#sns.set_palette("YlGn")
sns.set_palette("rocket")


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
            df['CO2 emissions (kt)'] = (1-alpha) * df[f"{year}"] + alpha * df[f"{year+1}"]
            df.sort_values('CO2 emissions (kt)', ascending=False, inplace=True)
            bars.append((year if alpha < 1 else year+1,
                         df['Country Name'].head(20).tolist(),
                         df['CO2 emissions (kt)'].head(20).tolist()))
    return bars


def add_image(
        ax:matplotlib.axes.Axes,
        name:str, zoom:float, xybox:tuple[float,float]
    ) -> matplotlib.offsetbox.AnnotationBbox:
    try:
        image = plt.imread(f"flags/{name}.png")
    except Exception as ex:
        print(name)
        raise(ex)
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
        plt.title(f"CO2 Emissions (kt) Year: {year}", fontsize=50)
        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_visible(False)
        for l in ax.get_yticklabels():
            l.set_fontsize(20)
        plt.tick_params(left=False, bottom=False, labelbottom=False)
        width=max([bar.get_width() for bar in barC])
        for country, bar in zip(countries, barC):
            ax.text(
                bar.get_width(),
                bar.get_y() + .2 * bar.get_height(),
                f"  {bar.get_width():.0f}", va='center',
                fontsize=20,
            )
            add_image(
                plt.gca(),
                country,
                .25,
                (bar.get_width() + .09*width, bar.get_y() + .5*bar.get_height())
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

if __name__ == "__main__":
    df = pd.read_csv("API_EN.ATM.CO2E.KT_DS2_en_csv_v2_2163797.csv", skiprows=4)
    for x in [
        "World",
        "IDA & IBRD total",
        "Low & middle income",
        "Middle income",
        "IBRD only",
        "Upper middle income",
        "High income",
        "Late-demographic dividend",
        "OECD members",
        "East Asia & Pacific",
        "Post-demographic dividend",
        "Europe & Central Asia",
        "Early-demographic dividend",
        "North America",
        "Lower middle income",
        "European Union",
        "Euro area",
        "Middle East & North Africa",
        "South Asia",
        "Latin America",
        "Sub-Saharan Africa",
        "IDA total",
        "Central Europe and the Baltics",
        "Fragile and conflict affected situations",
        "IDA blend",
        "Pre-demographic dividend",
        "IDA only",
        "Least developed countries",
        "Low income",
    ]:
        df = df[~df['Country Name'].str.contains(x)]
    df['Country Name'] = df['Country Name']\
        .apply(lambda s: "Iran" if s=="Iran, Islamic Rep." \
                                 else "South Korea" if s=="Korea, Rep." \
                                 else "North Korea" if s=="Korea, Dem. People’s Rep." \
                                 else s)
    make_anim(get_bars(df, 1960, 2020))
    run("bash add_music_and_export.sh", shell=True, capture_output=True, check=True)
