"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
Gatech OMSCS CS 7646
Autumn 2018
Homework Assignment - Strategy Learner
Haohao Wang (hwang404)
"""

import datetime as dt
import pandas as pd
import util as ut
import random
from QLearner import QLearner
import indicators
import numpy as np

class StrategyLearner(object):

    # constructor
    def __init__(self, verbose = False, impact=0.0):
        self.verbose = verbose
        self.impact = impact

        self.learner = QLearner(num_states=1000, \
        num_actions = 3, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False)




    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "JPM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,12,31), \
        sv = 100000):

        dates = pd.date_range(sd, ed)
        prices = ut.get_data([symbol], dates)[[symbol]]
        prices['Cash'] = 1.0
        high = ut.get_data([symbol], dates, colname = 'High')[[symbol]]
        low = ut.get_data([symbol], dates, colname = 'Low')[[symbol]]
        orig_close = ut.get_data([symbol], dates, colname = 'Close')[[symbol]]
        adj_high = high * prices[[symbol]] / orig_close
        adj_low = low * prices[[symbol]] / orig_close

        orders = pd.DataFrame().reindex_like(prices)
        orders = orders.rename(index=str, columns={'Cash': 'Order', symbol:'Shares'})
        orders['Shares'] = 0
        orders['Order'] = 'CASH'
        orders.index.name = 'Date'
        orders.index = pd.to_datetime(orders.index, format="%Y/%m/%d")

        positions = pd.DataFrame().reindex_like(prices)
        positions.fillna(0, inplace=True)
        positions.iloc[0, -1] = sv
        action = self.learner.querysetstate(0)

        sma_range = indicators.sma(prices[[symbol]], 10).iloc[:, 0]
        sma_bins = pd.qcut(sma_range, 10, labels=False)
        bb_range = indicators.bb(prices[[symbol]])
        bb_range['value'] = bb_range.High - bb_range.Low
        bb_range.fillna(method='bfill', inplace=True)
        bb_range = bb_range['value']
        bb_bins = pd.qcut(bb_range, 10, labels=False)
        comparisons = [adj_high[symbol]-adj_low[symbol], abs(adj_low[symbol] - prices[symbol].shift(1)), abs(adj_high[symbol] - prices[symbol].shift(1))]
        tr = pd.concat(comparisons, axis=1).max(axis=1)
        tr.fillna(method='bfill', inplace=True)
        atr_range = tr.rolling(14, min_periods=1).mean()
        atr_bins = pd.qcut(atr_range, 10, labels=False)
        states = sma_bins * 100 + bb_bins * 10 + atr_bins
        states = atr_bins * 100 + bb_bins * 10 + sma_bins
        #states = pd.qcut(sma_range, 500, labels=False) # for experiment 1 to compare with manual strategy

        pre_shares = 0
        normalized_close = prices[symbol]/prices.iloc[0, 0]
        daily_return = normalized_close - normalized_close.shift(1)
        daily_return.fillna(method='bfill', inplace=True)
        pre_orders = orders.copy()
        pre_orders.iloc[0, 0] = 1000

        while not orders.equals(pre_orders): # check if converges
            pre_cash = sv
            pre_holdings = 0
            pre_orders = orders.copy()
            for date, row in orders.iterrows():
                cur_state = states[date]
                reward = daily_return[date] * pre_holdings * (1 - self.impact)
                action = self.learner.query(cur_state, reward)
                orders.loc[date, 'Order'] = action
                if action == 0:
                    orders.loc[date, 'Shares'] = -1000 - pre_shares
                    positions.loc[date, symbol] = -1000
                if action == 1:
                    orders.loc[date, 'Shares'] = 0 - pre_shares
                    positions.loc[date, symbol] = 0
                if action == 2:
                    orders.loc[date, 'Shares'] = 1000 - pre_shares
                    positions.loc[date, symbol] = 1000

                positions.loc[date, 'Cash'] = pre_cash - orders.loc[date, 'Shares'] * prices.loc[date, symbol]
                pre_cash = positions.loc[date, 'Cash']
                pre_holdings = positions.loc[date, symbol]
            #cur_return = ((positions * prices).sum(axis=1).iloc[-1] - sv )/sv

        # add your code to do learning here

        # example usage of the old backward compatible util function
        # syms=[symbol]
        # dates = pd.date_range(sd, ed)
        # prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        # prices = prices_all[syms]  # only portfolio symbols
        # prices_SPY = prices_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print prices

        # example use with new colname
        # volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
        # volume = volume_all[syms]  # only portfolio symbols
        # volume_SPY = volume_all['SPY']  # only SPY, for comparison later
        # if self.verbose: print volume

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "JPM", \
        sd=dt.datetime(2010,1,1), \
        ed=dt.datetime(2011,12,31), \
        sv = 100000):

        dates = pd.date_range(sd, ed)
        prices = ut.get_data([symbol], dates)[[symbol]]
        high = ut.get_data([symbol], dates, colname = 'High')[[symbol]]
        low = ut.get_data([symbol], dates, colname = 'Low')[[symbol]]
        orig_close = ut.get_data([symbol], dates, colname = 'Close')[[symbol]]
        adj_high = high * prices[[symbol]] / orig_close
        adj_low = low * prices[[symbol]] / orig_close

        sma_range = indicators.sma(prices[[symbol]], 10).iloc[:, 0]
        sma_bins = pd.qcut(sma_range, 10, labels=False)
        bb_range = indicators.bb(prices[[symbol]])
        bb_range['value'] = bb_range.High - bb_range.Low
        bb_range.fillna(method='bfill', inplace=True)
        bb_range=bb_range['value']
        bb_bins = pd.qcut(bb_range, 10, labels=False)
        comparisons = [adj_high[symbol]-adj_low[symbol], abs(adj_low[symbol] - prices[symbol].shift(1)), abs(adj_high[symbol] - prices[symbol].shift(1))]
        tr = pd.concat(comparisons, axis=1).max(axis=1)
        tr.fillna(method='bfill', inplace=True)
        atr_range = tr.rolling(14, min_periods=1).mean()
        atr_bins = pd.qcut(atr_range, 10, labels=False)
        states = sma_bins * 100 + bb_bins * 10 + atr_bins
        states = atr_bins * 100 + bb_bins * 10 + sma_bins
        #states = pd.qcut(sma_range, 1000, labels=False) # for experiment 1 to compare with manual strategy
        trades = prices.copy()
        pre_position = 0
        for date, row in trades.iterrows():
            cur_state = states[date] # compute current state
            action = self.learner.querysetstate(cur_state)
            if action == 0:
                trades.loc[date, symbol] = -1000 - pre_position
                pre_position = -1000
            elif action == 1:
                trades.loc[date, symbol] = 0 - pre_position
                pre_position = 0
            elif action == 2:
                trades.loc[date, symbol] = 1000 - pre_position
                pre_position = 1000
        # here we build a fake set of trades
        # your code should return the same sort of data
        # dates = pd.date_range(sd, ed)
        # prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        # trades = prices_all[[symbol,]]  # only portfolio symbols
        # trades_SPY = prices_all['SPY']  # only SPY, for comparison later
        # trades.values[:,:] = 0 # set them all to nothing
        # trades.values[0,:] = 1000 # add a BUY at the start
        # trades.values[40,:] = -1000 # add a SELL
        # trades.values[41,:] = 1000 # add a BUY
        # trades.values[60,:] = -2000 # go short from long
        # trades.values[61,:] = 2000 # go long from short
        # trades.values[-1,:] = -1000 #exit on the last day
        if self.verbose: print(type(trades)) # it better be a DataFrame!
        if self.verbose: print(trades)
        if self.verbose: print(prices_all)
        return trades

        def author(self):
            return 'hwang404'

if __name__=="__main__":
    print ("One does not simply think up a strategy")
