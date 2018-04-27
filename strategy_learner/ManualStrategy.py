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
import indicators

def testPolicy(symbol=["JPM"], sd=dt.datetime(2010,1,1), ed=dt.datetime(2011,12,31), sv=100000):
    prices = get_data(['JPM'], pd.date_range(sd, ed), addSPY=True, colname = 'Adj Close')

    # mean_5 = indicators.mean_2(prices)
    # mean_5 = mean_5[19:]
    orders = pd.DataFrame().reindex_like(prices)
    orders = orders.rename(index=str, columns={"SPY":"Position", "JPM":"Symbol"})
    orders['Symbol'] = 'JPM'
    orders['Shares'] = 0
    orders['Position'] = 0
    orders['Order'] = 'HOLD'
    orders.index.name = 'Date'
    orders.index = pd.to_datetime(orders.index, format="%Y/%m/%d")

    # # SMA
    # sma_20 = indicators.sma(prices, 20)
    # sma_5 = indicators.sma(prices, 5)
    # for date, row in orders.iloc[2:, :].iterrows():
    #     stock = row['Symbol']
    #     i = orders.index.get_loc(date)
    #     p0 = prices.iloc[i, 1]
    #     sma_5_1 = sma_5.iloc[i-1, 1]
    #     sma_20_1 = sma_20.iloc[i-1, 1]
    #     sma_5_2 = sma_5.iloc[i-2, 1]
    #     sma_20_2 = sma_20.iloc[i-2, 1]
    #     current = row['Position']
    #     if sma_5_1 < sma_20_1 and sma_5_2 > sma_20_2: # buy
    #         target = min(1000, sv // p0 + current)
    #         orders.loc[date, 'Shares'] = target - current
    #         orders.loc[date, 'Position'] = target
    #         orders.loc[date, 'Order'] = 'BUY'
    #         sv -= (target - current) * p0
    #     elif sma_5_1 > sma_20_1 and sma_5_2 < sma_20_2:
    #         target = min(1000, sv // p0 + current)
    #         orders.loc[date, 'Shares'] = target - current
    #         orders.loc[date, 'Position'] = -target
    #         orders.loc[date, 'Order'] = 'SELL'
    #         sv += (target - current) * p0
    #     else:
    #         orders.loc[date, 'Shares'] = 0
    #         orders.loc[date, 'Position'] = current
    #         orders.loc[date, 'Order'] = 'HOLD'
    #SMA
    sma = indicators.sma(prices, 10)
    for date, row in orders.iloc[2:, :].iterrows():
        stock = row['Symbol']
        i = orders.index.get_loc(date)
        p0 = prices.iloc[i, 1]
        p1 = prices.iloc[i-1, 1]
        ma1 = sma.iloc[i-1, 1]
        p2 = prices.iloc[i-2, 1]
        ma2 = sma.iloc[i-2, 1]
        current = row['Position']
        if p1 < ma1 * 0.95: # buy
            target = min(1000, sv // p0 + current)
            orders.loc[date, 'Shares'] = target - current
            orders.loc[date, 'Position'] = target
            orders.loc[date, 'Order'] = 'BUY'
            sv -= (target - current) * p0
        elif p1 > ma1 * 1.05:
            target = min(1000, sv // p0 + current)
            orders.loc[date, 'Shares'] = target - current
            orders.loc[date, 'Position'] = -target
            orders.loc[date, 'Order'] = 'SELL'
            sv += (target - current) * p0
        else:
            orders.loc[date, 'Shares'] = 0
            orders.loc[date, 'Position'] = current
            orders.loc[date, 'Order'] = 'HOLD'
    return orders

def getBenchmark(sd, ed, shares=1000, symbol='JPM'):
    benchmark = get_data([symbol], pd.date_range(sd, ed))
    benchmark = benchmark[symbol] * shares + 100000 - benchmark.iloc[0, 1] * 1000
    return benchmark

if __name__ == '__main__':
    start_date = dt.datetime(2010,1,1)
    end_date = dt.datetime(2011,12,31)
    starting_value = 100000
    orders = testPolicy(symbol=["JPM"], sd=start_date, ed=end_date, sv=starting_value)
    benchmark = ml.getBenchmark(shares=1000, sd=start_date, ed=end_date, symbol=['JPM'])
    benchmark = benchmark / benchmark.iloc[0]
    manual_str = compute_portvals(orders, start_val = starting_value, commission=9.95, impact=0.005)
    manual_str = manual_str / manual_str.iloc[0]
    ax = benchmark.plot(x=None, y='JPM', color='blue')
    ax = manual_str.plot(y='PortVal', ax=ax, color='black')
    ymin, ymax = ax.get_ylim()
    ax.vlines(x=orders[orders['Order'] == 'BUY'].index, ymin=ymin, ymax=ymax, color='g', lw=0.2)
    ax.vlines(x=orders[orders['Order'] == 'SELL'].index, ymin=ymin, ymax=ymax, color='r', lw=0.2)
    ax.legend(["Benchmark", "Manual Strategy"])
    plt.show()
