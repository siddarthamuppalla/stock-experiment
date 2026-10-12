import pandas as pd
import pytest
from engine import backtest, metrics

def prices():
    return pd.DataFrame({"Open":[100.,110.,120.],"Close":[105.,115.,125.]})

def test_intraday():
    r=backtest(prices())["intraday"]
    assert r.iloc[0]==pytest.approx(.05)

def test_overnight():
    r=backtest(prices())["overnight"]
    assert r.iloc[0]==0
    assert r.iloc[1]==pytest.approx(110/105-1)

def test_compounding():
    r=backtest(prices())["buy_hold"]
    assert (1+r).prod()==pytest.approx(1.25)

def test_costs_reduce_returns():
    gross=backtest(prices())["intraday"]
    net=backtest(prices(),10)["intraday"]
    assert (net<gross).all()

def test_metrics():
    assert metrics(pd.Series([.1,-.1]))["total_return"]==pytest.approx(-.01)
