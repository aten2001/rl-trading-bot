"""
Gatech OMSCS CS 7646
Autumn 2018
Homework Assignment - Manual Strategy
Haohao Wang (hwang404)
"""

from util import get_data
import pandas as pd
import datetime as dt
import numpy as np
from marketsimcode import compute_portvals
import matplotlib.pyplot as plt

def atr(adj_high, adj_low, adj_close):
    tr = pd.DataFrame([adj_high - adj_low, abs(adj_low - adj_close.shift(1)), abs(adj_high - adj_close.shift(1))]).max()
    res = tr.rolling(14).mean()
    res = res['2008-01-01':]
    res.columns = ['ATR']
    return res

def sma(adj_close, window):
    res = adj_close.rolling(window, min_periods=1).mean()
    return res

def bb(adj_close):
    mean_20 = mean_1(adj_close)
    mean_20 = mean_20['2008-01-01':]
    std = adj_close.rolling(20).std()
    std = std['2008-01-01':]
    bb_up = mean_20 + std * 2
    bb_low = mean_20 - std * 2
    ret = pd.concat([bb_up,bb_low], axis=1)
    ret.columns = ["Bollinger Band High", "Bollinger Band Low"]
    return ret

if __name__ == '__main__':
    start_date = dt.datetime(2007,1,1)
    end_date = dt.datetime(2010,1,4)
    adj_close = get_data(['JPM'], pd.date_range(start_date, end_date), addSPY=True, colname = 'Adj Close')['JPM']
    close = get_data(['JPM'], pd.date_range(start_date, end_date), addSPY=True, colname = 'Close')['JPM']
    ratio = adj_close / close

    low = get_data(['JPM'], pd.date_range(start_date, end_date), addSPY=True, colname = 'Low')['JPM']
    adj_low = low * ratio

    high = get_data(['JPM'], pd.date_range(start_date, end_date), addSPY=True, colname = 'High')['JPM']
    adj_high = high * ratio

    #20 DAY SMA
    adj_close = adj_close['2008-01-01':]
    ax = adj_close['2008-01-01':].plot(x=None, y='JPM')
    mean_20 = sma(adj_close, 20)
    mean_20.plot(y='JPM', ax=ax)
    ax.legend(["Adjusted Close", "20-day SMA"])
    plt.show()

    #Bollinger Band
    ax = adj_close['2008-01-01':].plot(x=None, y='JPM')
    mean_20 = sma(adj_close, 20)
    mean_20.plot(y='JPM', ax=ax)
    bollBand = bb(adj_close)
    bollBand["Bollinger Band High"].plot(y='JPM', ax=ax)
    bollBand["Bollinger Band Low"].plot(y='JPM', ax=ax)
    ax.legend(["Adjusted Close", "SMA", "Bollinger Band Upper", "Bollinger Band Lower"])
    plt.show()

    # ATR
    diff = adj_close - adj_close.shift(1)
    ax = diff['2008-01-01':].plot(x=None, y='JPM')
    atr = atr(adj_high, adj_low, adj_close)
    atr.plot(y='ATR', ax=ax)
    negATR = atr * -1
    atr.columns = ['Negative ATR']
    negATR.plot(y='ATR', ax=ax)
    ax.legend(["Price Diff", "ATR", "Negative ATR"])
    plt.show()

    #Double SMA
    ax = adj_close['2008-01-01':].plot(x=None, y='JPM')
    mean_20 = sma(adj_close, 20)
    mean_5 = sma(adj_close, 5)
    mean_20.plot(y='JPM', ax=ax)
    mean_5.plot(y='JPM', ax=ax)
    ax.legend(["Adjusted Close", "20-day SMA", "5-day SMA"])
    plt.show()
