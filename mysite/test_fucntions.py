#Here we test out all our functions

import matplotlib.pyplot as plt, mpld3
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.finance import candlestick_ohlc

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

import numpy as np
import pandas as pd
import MySQLdb

import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook


####How to create a graph for html
def test_graph():
    plt.plot([3,1,4,1,5], 'ks-', mec='w', mew=5, ms=20)
    mpld3.show()

###how to take sql data to a plot
def mysql_select_all():
    conn = MySQLdb.connect(host='localhost',
                           user='root',
                           passwd='pickle',
                           db='pickledb')
    cursor = conn.cursor()
    sql = "SELECT Close FROM ddr"
    cursor.execute(sql)
    result = cursor.fetchall()
    df = pd.DataFrame(list(result),columns=["Close"])
    x = df.Close
    plt.title("Table", fontsize="24")
    plt.plot(x)
    plt.xlabel("Size1")
    plt.tick_params(axis='both',which='major',labelsize=14)
    plt.show()
    cursor.close()


####How to create live graphs
def animate(ax1):
    xs = [1,2,3,4,5,6]
    xy = [1,3,4,6,2,3]
    ax1.clear()
    ax1.plot(xs,xy)
def live_graph():
    style.use('fivethirtyeight')
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ani = animation.FuncAnimation(fig, animate(ax1), interval=1000)
    plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def button_graph():
    freqs = np.arange(2, 20, 3)

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    t = np.arange(0.0, 1.0, 0.001)
    s = np.sin(2*np.pi*freqs[0]*t)
    l, = plt.plot(t, s, lw=2)


    class Index(object):
        ind = 0

        def next(self, event):
            self.ind += 1
            i = self.ind % len(freqs)
            ydata = np.sin(2*np.pi*freqs[i]*t)
            l.set_ydata(ydata)
            plt.draw()

        def prev(self, event):
            self.ind -= 1
            i = self.ind % len(freqs)
            ydata = np.sin(2*np.pi*freqs[i]*t)
            l.set_ydata(ydata)
            plt.draw()

    callback = Index()
    axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Next')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, 'Previous')
    bprev.on_clicked(callback.prev)

    plt.show()




#mysql_select_all()
#button_graph()

    #####################
    #Do Dates properly
    #####################


    # load a numpy record array from yahoo csv data with fields date,
    # open, close, volume, adj_close from the mpl-data/example directory.
    # The record array stores python datetime.date as an object array in
    # the date column
    # datafile = cbook.get_sample_data('goog.npy')
def candle_date():
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    # load a numpy record array from yahoo csv data with fields date,
    # open, close, volume, adj_close from the mpl-data/example directory.
    # The record array stores python datetime.date as an object array in
    # the date column
    # datafile = cbook.get_sample_data('goog.npy')

    r_date =['2012-10-29','2012-10-30']

    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.plot(r_date, r.adj_close)


    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    datemin = datetime.date(r.date.min().year, 1, 1)
    datemax = datetime.date(r.date.max().year + 1, 1, 1)
    ax.set_xlim(datemin, datemax)

    # format the coords message box
    def price(x): return '$%1.2f' % x

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.format_ydata = price
    ax.grid(True)

    second = True
    if second:
        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        ax = fig.add_subplot(212)
        ax.plot(r.date, r.adj_close)

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        datemin = datetime.date(r.date.min().year, 1, 1)
        datemax = datetime.date(r.date.max().year + 1, 1, 1)
        ax.set_xlim(datemin, datemax)

        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.show()

    def ticker_list():
        with open('tickers.txt') as f:
            mlist = []
            for line in f:
                try:
                    line = line.replace('\r', '').replace('\n', '')
                    mlist.append(line)
                    print("Creating " + line)
                except:
                    pass
            print(mlist)
#candle_date()
ticker_list()