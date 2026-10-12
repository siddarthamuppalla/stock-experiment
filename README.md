# Stock Experiments

Dashboard: https://siddarthamuppalla.github.io/stock-experiment/

## Deploy
In Settings → Pages, set Source to **GitHub Actions**. Then run **Actions → Backtest and deploy → Run workflow**. It also refreshes on weekday evenings.

## Local use
```bash
pip install -r requirements.txt
python -m pytest -q
python run.py
python run.py --tickers AMD NVDA --cost-bps 5 --days 730
```

Strategies live in `engine.py` and are registered with `@strategy`. Returns compound and use adjusted daily OHLC; they are theoretical, not guaranteed executable fills. The S&P 500 index is not directly tradable. Trading costs are per side, in basis points.
