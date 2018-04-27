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

def testPolicy(symbol=["JPM"], sd=dt.datetime(2008,1,1), ed=dt.datetime(2010,1,4), sv=100000):
    start_date = sd
    end_date = ed
    prices = get_data(symbol, pd.date_range(start_date, end_date))
    orders = pd.DataFrame().reindex_like(prices)
    orders = orders.rename(index=str, columns={"SPY":"Position", "JPM":"Symbol"})
    orders['Symbol'] = 'JPM'
    orders['Shares'] = 0
    orders['Position'] = 0
    orders['Order'] = None
    orders.index.name = 'Date'
    orders.index = pd.to_datetime(orders.index, format="%Y/%m/%d")
    for date, row in orders.iloc[:-1,:].iterrows():
        stock = row['Symbol']
        next_day = orders.index.get_loc(date) + 1
        last_day = orders.index.get_loc(date) - 1
        if prices.loc[date, stock] < prices.iloc[next_day, 1] and prices.loc[date, stock] < prices.iloc[next_day, 1] and orders.loc[date,'Position'] != 1000:
            orders.loc[date, 'Shares'] = 1000 - orders.iloc[last_day, 0]
            orders.loc[date, 'Position'] = 1000
            orders.loc[date, 'Order'] = 'BUY'
        elif prices.loc[date, stock] > prices.iloc[next_day, 1] and orders.loc[date,'Position'] != -1000:
            orders.loc[date, 'Shares'] = 1000 + orders.iloc[last_day, 0]
            orders.loc[date, 'Position'] = -1000
            orders.loc[date, 'Order'] = 'SELL'
        else:
            orders.loc[date, 'Shares'] = 0
            orders.loc[date, 'Position'] = orders.iloc[last_day, 0]
            orders.loc[date, 'Order'] = 'HOLD'
    return orders

def getBenchmark(shares=1000, sd=dt.date(2008,1,1), ed=dt.date(2009,12,31), symbol=['JPM']):
    benchmark = get_data(symbol, pd.date_range(sd, ed))
    benchmark['JPM'] = benchmark['JPM'] * shares + 100000 - 38470
    return benchmark

if __name__ == '__main__':
    start_date = dt.datetime(2008,1,1)
    end_date = dt.datetime(2010,1,4)
    starting_value = 100000
    orders = testPolicy(symbol=["JPM"], sd=start_date, ed=end_date, sv=starting_value)
    benchmark = getBenchmark(shares=1000, sd=dt.date(2008,1,1), ed=dt.date(2009,12,31), symbol=['JPM'])
    benchmark = benchmark / benchmark.iloc[0]
    best_str = compute_portvals(orders, start_val = starting_value, commission=0, impact=0.000)[:-1]
    best_str = best_str / best_str.iloc[0]
    ax = benchmark.plot(x=None, y='JPM', color='blue')
    best_str.plot(y='PortVal', ax=ax, color='black')
    ax.legend(["Benchmark", "Best Strategy"])
    plt.show()
