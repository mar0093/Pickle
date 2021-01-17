from datetime import datetime, time
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.dates as dates
import matplotlib.pyplot as plt
from matplotlib import ticker
import mpl_finance
import MySQLdb
import matplotlib.dates as mdates

def plot_candles(title=None, volume_bars=False, color_function=None, technicals=None):
    def my_df():
        conn = MySQLdb.connect(host='localhost',
                               user='root',
                               passwd='pickle',  #
                               db='pickledb')  # falsified information
        cursor = conn.cursor()
        sql = "SELECT * FROM ddr"
        cursor.execute(sql)
        result = cursor.fetchall()
        df = pd.DataFrame(list(result), columns=["Date", "Open", "High", "Low", "Close", "Adj_Close", "Volume"])
        # fig, ax = plt.subplots()

        df["Date"] = [dt.datetime.strptime(d, '%Y-%m-%d') for d in df["Date"]]
        df = df.set_index(df["Date"])
        # ax.plot_date(df.index, df["Volume"], fmt='o', tz=None, xdate=True)
        # plt.show()
        return df
    """ Plots a candlestick chart using quantopian pricing data.

    Author: Daniel Treiman

    Args:
      pricing: A pandas dataframe with columns ['open_price', 'close_price', 'high', 'low', 'volume']
      title: An optional title for the chart
      volume_bars: If True, plots volume bars
      color_function: A function which, given a row index and price series, returns a candle color.
      technicals: A list of additional data series to add to the chart.  Must be the same length as pricing.
    """
    pricing = my_df()
    def default_color(index, open_price, close_price,low, high):
        return 'r' if open_price[index] > close_price[index] else 'g'

    color_function = color_function or default_color
    technicals = technicals or []
    open_price = pricing["Open"]
    close_price = pricing["Close"]
    low = pricing["Low"]
    high = pricing['High']
    oc_min = pd.concat([open_price, close_price], axis=1).min(axis=1)
    oc_max = pd.concat([open_price, close_price], axis=1).max(axis=1)
    if volume_bars:
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax1 = plt.subplots(1, 1)
    if title:
        ax1.set_title(title)
    x = np.arange(len(pricing))
    candle_colors = [color_function(i, open_price, close_price, low, high) for i in x]
    candles = ax1.bar(x, oc_max - oc_min, bottom=oc_min, color=candle_colors, linewidth=0)
    lines = ax1.vlines(x + 0.4, low, high, color=candle_colors, linewidth=1)
    ax1.xaxis.grid(False)
    ax1.xaxis.set_tick_params(which='major', length=3.0, direction='in', top='off')
    ax1.locator_params(nbins=4, axis='x')
    # Assume minute frequency if first two bars are in the same day.
    #frequency = 'minute' if (pricing.index[1] - pricing.index[0]).days == 0 else 'day'
    time_format = '%d-%m-%Y'
    #if frequency == 'minute':
      #  time_format = '%H:%M'
    # Set X axis tick labels.
    lpi= len(pricing.index)
    eight_bits = lpi//6
    #plt.xticks(np.arange(0,lpi,eight_bits), [date.strftime(time_format) for date in pricing.index[0::eight_bits]])


    #months = mdates.MonthLocator()  # every month
    #yearsFmt = mdates.DateFormatter('%Y')

    #ax1.xaxis.set_major_formatter(yearsFmt)
    #ax1.xaxis.set_minor_locator(months)
    # years = mdates.YearLocator()
    # ax1.xaxis.set_major_locator(years)
    plt.xticks(x, [date.strftime(time_format) for date in pricing.index]) #NEED THIS FOR ORIGINAL
    pricing["Close_av_100"] = pricing['Close'].rolling(100).mean()
    #pricing["Close_av_100"] = pd.rolling_mean(pricing["Close"],100)
    ax1.plot(x, pricing["Close_av_100"])
    #N = len(pricing.index)
    #ind = np.arange(N)  # the evenly spaced plot indices

#    def format_date(x, pos=None):
 #       thisind = np.clip(int(x + 0.5), 0, N - 1)
  #      return pricing.index[thisind].strftime('%Y-%m-%d')

    for indicator in technicals:
        ax1.plot_date(x, indicator, xdate=True)




    if volume_bars:
        volume = pricing['Volume']
        volume_scale = None
        scaled_volume = volume
        if volume.max() > 1000000:
            volume_scale = 'M'
            scaled_volume = volume / 1000000
        elif volume.max() > 1000:
            volume_scale = 'K'
            scaled_volume = volume / 1000
        ax2.bar(x, scaled_volume, color=candle_colors)
        volume_title = 'Volume'
        if volume_scale:
            volume_title = 'Volume (%s)' % volume_scale
        ax2.set_title(volume_title)
        ax2.xaxis.grid(False)
        ax2.xaxis.set_major_locator(ticker.LinearLocator())
    return plt.show()


plot_candles(volume_bars=False)

