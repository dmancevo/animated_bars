from typing import Callable
import argparse
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


def _get_df(stonk:str, start_date:date, end_date:date, **kwargs) -> pd.DataFrame:
    url = (f"https://query1.finance.yahoo.com/v7/finance/download/{stonk}"
           f"?period1={int(start_date.timestamp())}"
           f"&period2={int(end_date.timestamp())}&interval=1d"
            "&events=history&includeAdjustedClose=true")
    return pd.read_csv(url).assign(Ticker=stonk)


def get_df(stonks:list[str], start_date:str, end_date:str=None, **kwargs) -> pd.DataFrame:
    start_date = datetime.combine(date.fromisoformat(start_date), datetime.min.time())
    end_date = datetime.now() if end_date is None \
        else datetime.combine(date.fromisoformat(end_date), datetime.min.time())
    return pd.concat([_get_df(stonk, start_date, end_date) \
        for stonk in stonks])


def add_shares(df:pd.DataFrame, initial_amount:float, monthly_amount:float) -> pd.DataFrame:
    shares = {}
    invested = set([])
    new_df = []
    for i,row in df.assign(date=lambda x: pd.to_datetime(x.Date)).iterrows():
        K = (row.Ticker, row.date.year, row.date.month)
        if row.Ticker not in shares:
            shares[row.Ticker] = initial_amount/row.Close
        if K not in invested:
            shares[row.Ticker] += monthly_amount/row.Close
            invested.add(K)
        row['Shares'] = shares[row.Ticker]
        new_df.append(row)
    return pd.DataFrame(new_df).drop('date', axis=1)


def get_update_f(df:pd.DataFrame, metric:str, timeframes:list[date],
                    colors:list[tuple[float]]) -> Callable[[int], None]:
    df.sort_values(['Date', metric], inplace=True)
    def update(i):
        nonlocal df, timeframes
        curr_date = timeframes[i]
        _df = df[df.Date == curr_date]
        _df.assign(Rank = lambda x: x[metric].rank()).sort_values('Rank')
        plt.cla()
        bars = plt.barh(
            _df.Ticker, _df[metric],
            color=[colors[t] for t in _df.Ticker.unique()],
            alpha=0.7,
        )
        plt.title((
            f"{date.fromisoformat(curr_date).strftime('%Y %b')}"
            f"    Total Amount: ${_df.Value.sum():.2f}"
            ), fontsize=50)
        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_visible(False)
        for l in ax.get_yticklabels():
            l.set_fontsize(40)
        plt.tick_params(left=False, bottom=False, labelbottom=False)
        for bar in bars:
            ax.text(
                bar.get_width(),
                bar.get_y() + bar.get_height()/2,
                f"  ${bar.get_width():.0f}", va='center',
                fontsize=40,
            )
    return update


def make_anim(df:pd.DataFrame, metric:str, file_name:str="mov.mp4", **kwargs):
    timeframes = df.Date.unique()
    tickers = df.Ticker.unique().tolist()
    colors = {t:c for t,c in zip(tickers, sns.color_palette()[:len(tickers)])}
    fig = plt.figure(figsize=[20,12])
    anim = FuncAnimation(fig,
        get_update_f(df=df, metric=metric, timeframes=timeframes,
                        colors=colors, **kwargs),
        interval=200, frames=len(timeframes), repeat=False
    )
    anim.save(file_name, writer='ffmpeg')
    shutil.move(file_name, "/Users/dmancevo/Downloads/mov.mp4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stonks", type=lambda s: [x.strip() for x in s.split(',')])
    parser.add_argument("--start_date", "-s", default=f"{date.today() - timedelta(days=365)}")
    parser.add_argument("--end_date", "-e", default=f"{date.today()}")
    parser.add_argument("--initial_amount", "-a", type=float, default=0.)
    parser.add_argument("--monthly_amount", "-m", type=float, default=100.)
    args = parser.parse_args()
    df = (
        get_df(**dict(args._get_kwargs()))
        .set_index('Date')
        .groupby('Ticker')
        .rolling(7)
        .Close
        .mean()
        .reset_index()
        .dropna()
    )
    df.sort_values("Date", inplace=True)
    df = add_shares(df, args.initial_amount, args.monthly_amount)
    df['Value'] = df.Shares * df.Close
    make_anim(df, 'Value')
