import numpy as np
import pandas as pd

STRATEGIES = {}
def strategy(name):
    def register(fn):
        STRATEGIES[name] = fn
        return fn
    return register

@strategy("overnight")
def overnight(df):
    return (df.Open / df.Close.shift(1) - 1).fillna(0)

@strategy("intraday")
def intraday(df):
    return df.Close / df.Open - 1

@strategy("buy_hold")
def buy_hold(df):
    r = df.Close.pct_change()
    r.iloc[0] = df.Close.iloc[0] / df.Open.iloc[0] - 1
    return r

def backtest(df, cost_bps=0, strategies=None):
    if len(df)<2 or not {"Open","Close"}.issubset(df.columns):
        raise ValueError("At least two sessions required")
    if df[["Open","Close"]].isna().any().any() or (df[["Open","Close"]]<=0).any().any():
        raise ValueError("Invalid prices")
    fee = cost_bps / 10000
    if not 0<=fee<1: raise ValueError("Invalid fee")
    out = pd.DataFrame(index=df.index)
    for name in (strategies or STRATEGIES):
        r = STRATEGIES[name](df).copy()
        if name == "buy_hold":
            r.iloc[0] = (1+r.iloc[0])*(1-fee)-1
            r.iloc[-1] = (1+r.iloc[-1])*(1-fee)-1
        elif name == "overnight":
            r.iloc[1:] = (1+r.iloc[1:])*(1-fee)**2-1
        else:
            r = (1+r)*(1-fee)**2-1
        out[name] = r
    return out

def metrics(r):
    r = pd.Series(r).dropna()
    eq = (1+r).cumprod()
    peak = np.maximum.accumulate(np.r_[1.,eq.to_numpy()])[1:]
    std = r.std(ddof=1)
    return dict(total_return=float(eq.iloc[-1]-1),
        annualized_return=float(eq.iloc[-1]**(252/len(r))-1) if eq.iloc[-1]>0 else -1.,
        volatility=float(std*np.sqrt(252)),
        sharpe_0rf=float(r.mean()/std*np.sqrt(252)) if std>0 else 0.,
        max_drawdown=float((eq/peak-1).min()),
        win_rate=float((r>0).mean()),sessions=int(len(r)))
