"""MC1-P2: Optimize a portfolio.

Copyright 2017, Georgia Tech Research Corporation
Atlanta, Georgia 30332-0415
All Rights Reserved
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from util import get_data, plot_data
from scipy.optimize import minimize

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def fun_to_opt(weights, data):
    rets = data/data.shift(1)
    return np.sqrt(np.dot(weights.T, np.dot(rets.cov(), weights)))

def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=True):
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
    nos = len(syms)
    cons = ({'type':'eq', 'fun':lambda x: np.sum(x) - 1})
    bnds = tuple((0, 1) for x in range(nos))
    sp = [1.0 / nos] * nos
    ops = minimize(fun_to_opt, sp, (prices,), method='SLSQP', bounds=bnds, constraints=cons) # add code here to find the allocations
    # add code here to compute stats
    # Get daily portfolio value
    sf = 252
    rfr = 0.0
    sv = 1.0
    allocs = ops['x'].round(3)
    relatives = prices / prices.ix[0]
    daily_portfolio = (relatives * allocs).sum(axis=1)
    # Get portfolio statistics (note: std_daily_ret = volatility)
    daily_ret = daily_portfolio/daily_portfolio.shift(1)
    cr = daily_portfolio[-1] / daily_portfolio[0] - 1
    adr = daily_ret.mean()
    sddr = daily_ret.std()
    sr = np.sqrt(sf) * (adr - rfr) / sddr

    # Get daily portfolio value
    port_val = daily_portfolio * sv # add code here to compute daily portfolio values

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        prices_SPY = prices_SPY / prices_SPY.ix[0]
        df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        plot_data(df_temp[['Portfolio', 'SPY']], title="Daily Portfolio Value and SPY", xlabel="Date", ylabel="Normalized Price")

    return allocs, cr, adr, sddr, sr

def test_code():
    # This function WILL NOT be called by the auto grader
    # Do not assume that any variables defined here are available to your function/code
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    start_date = dt.datetime(2008,6,1)
    end_date = dt.datetime(2009,6,1)
    symbols = ['IBM', 'X', 'GLD']

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        gen_plot = True)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr

if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()
