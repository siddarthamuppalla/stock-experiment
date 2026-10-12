import argparse, json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
import pandas as pd
import yfinance as yf
from engine import backtest, metrics, STRATEGIES

DEFAULT=["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","^GSPC"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tickers",nargs="+",default=DEFAULT)
    p.add_argument("--cost-bps",type=float,default=0)
    p.add_argument("--days",type=int,default=365)
    p.add_argument("--strategies",nargs="+",choices=list(STRATEGIES),default=list(STRATEGIES))
    args=p.parse_args()
    end=date.today()+timedelta(days=1)
    start=end-timedelta(days=args.days+1)
    rows=[]; series={}; errors={}
    for ticker in args.tickers:
        try:
            df=yf.download(ticker,start=str(start),end=str(end),auto_adjust=True,progress=False,multi_level_index=False,threads=False)
            if df.empty: raise ValueError("No data returned")
            df=df[["Open","Close"]].dropna()
            if len(df)<2: raise ValueError("Insufficient data")
            daily=backtest(df,args.cost_bps,args.strategies)
            series[ticker]={name:{"dates":daily.index.strftime("%Y-%m-%d").tolist(),
                "equity":(1+daily[name]).cumprod().round(10).tolist()} for name in daily}
            for name in daily:
                rows.append({"ticker":ticker,"strategy":name,**metrics(daily[name])})
        except Exception as exc:
            errors[ticker]=str(exc)
            print(f"ERROR {ticker}: {exc}",flush=True)
    if not rows: raise SystemExit("No market data available; refusing to publish fabricated results")
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"start":str(start),"end":str(end),
        "cost_bps":args.cost_bps,"summary":rows,"series":series,"errors":errors}
    out=Path("docs/data/results.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,allow_nan=False,separators=(",",":")))
    pd.DataFrame(rows).to_csv("docs/data/summary.csv",index=False)
    print(pd.DataFrame(rows)[["ticker","strategy","total_return","max_drawdown"]].to_string(index=False))
if __name__=="__main__": main()
