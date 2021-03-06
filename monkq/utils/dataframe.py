#
# MIT License
#
# Copyright (c) 2018 WillQ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import datetime
from typing import Any, List, Union

import pandas
import talib
from dateutil.relativedelta import relativedelta
from matplotlib.axes import Axes
from matplotlib.dates import AutoDateLocator, DateFormatter, date2num
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from monkq.config.global_settings import KLINE_SIDE_CLOSED, KLINE_SIDE_LABEL
from pandas.tseries.frequencies import to_offset
from talib import abstract


def is_datetime_not_remain(obj: datetime.datetime, freq: str) -> bool:
    offset = to_offset(freq)
    return obj.timestamp() % offset.delta.total_seconds() == 0


def make_datetime_exactly(obj: datetime.datetime, freq: str, forward: bool) -> datetime.datetime:
    if is_datetime_not_remain(obj, freq):
        return obj
    else:
        offset = to_offset(freq)

        remain = obj.timestamp() % offset.delta.total_seconds()

        if forward:
            relat = relativedelta(seconds=offset.delta.total_seconds() - remain)
        else:
            relat = relativedelta(seconds=-remain)

        outcome = obj + relat
        return outcome


def kline_count_window(df: pandas.DataFrame, endtime: datetime.datetime, count: int) -> pandas.DataFrame:
    freq = df.index.freq.freqstr

    if is_datetime_not_remain(endtime, freq):
        starttime = endtime - df.index.freq.delta * (count - 1)
    else:
        starttime = endtime - df.index.freq.delta * count

    return df.loc[starttime:endtime]  # type: ignore


CONVERSION = {
    'high': 'max',
    'low': 'min',
    'open': 'first',
    'close': 'last',
    'volume': 'sum',
    'turnover': 'sum'
}


def kline_1m_to_freq(df: pandas.DataFrame, freq: str) -> pandas.DataFrame:
    result = df.resample(freq, closed=KLINE_SIDE_CLOSED, label=KLINE_SIDE_LABEL).apply(CONVERSION)
    return result


TA_FUNCTION = talib.get_functions()


def kline_indicator(df: pandas.DataFrame,
                    func: str, columns: List[str],
                    *args: Any, **kwargs: Any) -> pandas.DataFrame:
    assert func in TA_FUNCTION, "not a valid function for talib"
    func = abstract.Function(func)
    result = func(df, *args, price=columns, **kwargs)  # type:ignore
    return result


def kline_time_window(df: pandas.DataFrame, start_datetime: datetime.datetime,
                      end_datetime: datetime.datetime) -> pandas.DataFrame:
    return df.loc[start_datetime: end_datetime]  # type:ignore


def _adjust_axe_timeaxis_view(ax: Axes) -> Axes:
    locator = AutoDateLocator()
    daysFmt = DateFormatter("%y%m%d\n%H:%M")
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.autoscale_view()
    return ax


def plot_kline_candlestick(ax: Axes, df: pandas.DataFrame, colordown: str = 'r', colorup: str = 'g',
                           alpha: float = 1.0) -> Axes:
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown
    """

    figure: Figure = ax.figure
    f_width = figure.get_figwidth()

    bar_take_axes_size_percentage = 0.04

    bar_width = f_width * bar_take_axes_size_percentage / len(df) / ax.numCols
    offset = bar_width / 2.0

    lines = []
    patches = []
    for row in df.iterrows():
        t = date2num(row[0])
        data = row[1]
        close = data.close
        open = data.open
        high = data.high
        low = data.low
        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - offset, lower),
            width=bar_width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)

    return _adjust_axe_timeaxis_view(ax)


def plot_indicator(ax: Axes, df: Union[pandas.DataFrame, pandas.Series], alpha: float = 1) -> Axes:
    # line = Line2D()
    if isinstance(df, pandas.DataFrame):
        for column in df.iteritems():
            name, dataframe = column
            ax.plot(date2num(dataframe.index.to_pydatetime()), dataframe.values, label=name, alpha=alpha)
    elif isinstance(df, pandas.Series):
        ax.plot(date2num(df.index.to_pydatetime()), df.values, label='indicator', alpha=alpha)
    else:
        raise NotImplementedError()
    ax.legend()
    return _adjust_axe_timeaxis_view(ax)


def plot_volume(ax: Axes, kline: pandas.DataFrame, color: str = 'b', alpha: float = 1) -> Axes:
    figure: Figure = ax.figure
    f_width = figure.get_figwidth()
    bar_take_axes_size_percentage = 0.9
    bar_width = f_width * bar_take_axes_size_percentage / len(kline) / ax.numCols
    ax.bar(date2num(kline.index.to_pydatetime()), kline['volume'].values,
           color=color, alpha=alpha, width=bar_width)
    return _adjust_axe_timeaxis_view(ax)
