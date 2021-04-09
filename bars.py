from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import ssl
import shutil

ssl._create_default_https_context = ssl._create_unverified_context

sns.set_style("white")
sns.set_context("poster")
sns.set_palette("mako")

N = 200
df = pd.concat([pd.DataFrame(dict(
    y=np.clip(5+np.random.normal(i*1e-1,1,N).cumsum(), 1, None),
    date=[date(2020,1,1)+timedelta(days=i) for i in range(N)],
    elem=[e for _ in range(N)])) \
        for i, e in enumerate(['sonic','diego','sam','frodo','gendry','p1','p2','p3','p4','p5'])])


def get_update_f(df, cat_col, metric, order_col, timeframes, title=""):
    df.sort_values([order_col, metric], inplace=True)
    def update(i):
        nonlocal df, cat_col, metric, order_col, timeframes, title
        _df = df[df[order_col] == timeframes[i]]
        plt.cla()
        bars = plt.barh(_df[cat_col], _df[metric],
                    color=sns.color_palette()[:_df.shape[0]])
        plt.title(f"{_df[order_col].min()}")
        plt.suptitle(title)
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
    return update


def make_anim(df, order_col, file_name="mov.mp4", **kwargs):
    timeframes = df[order_col].unique()
    fig = plt.figure(figsize=[20,12])
    anim = FuncAnimation(fig,
        get_update_f(df=df, order_col=order_col, timeframes=timeframes, **kwargs),
        interval=100, frames=len(timeframes), repeat=False
    )
    anim.save(file_name, writer='ffmpeg')
    shutil.move(file_name, "/Users/dmancevo/Downloads/mov.mp4")
