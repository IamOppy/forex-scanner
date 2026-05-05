import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

PAIRS = ["GC=F",
    "EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X",
    "NZDUSD=X","EURGBP=X","EURJPY=X","GBPJPY=X","AUDJPY=X",
    "CADJPY=X","CHFJPY=X","EURAUD=X","EURNZD=X","GBPAUD=X",
    "GBPNZD=X","AUDNZD=X","NZDJPY=X","USDCHF=X","EURCHF=X"
]

def get_data(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

def calculate(df, rsi_len, ema_fast, ema_slow):
    try:
        close_price = df['Close']
        if isinstance(close_price, pd.DataFrame): close_price = close_price.iloc[:, 0]
        if len(df) < 50: return pd.DataFrame()

        df["RSI"] = ta.rsi(close_price, length=rsi_len)
        df["EMA_FAST"] = ta.ema(close_price, length=ema_fast)
        df["EMA_SLOW"] = ta.ema(close_price, length=ema_slow)
        df["MOM"] = ta.mom(close_price, length=10)
        return df.dropna()
    except: return pd.DataFrame()

def score(row):
    s = 0
    r, ef, es, m = float(row["RSI"]), float(row["EMA_FAST"]), float(row["EMA_SLOW"]), float(row["MOM"])
    if r > 60: s += 1
    elif r < 40: s -= 1
    if ef > es: s += 1
    else: s -= 1
    if m > 0: s += 1
    else: s -= 1
    return s

def label(score_val):
    if score_val >= 2: return "🔥 Strong Bullish"
    elif score_val == 1: return "Bullish"
    elif score_val == 0: return "Neutral"
    elif score_val == -1: return "Bearish"
    else: return "❄️ Strong Bearish"

def run_scanner(tf, bars, rsi_len, ema_fast, ema_slow):
    results = []
    print(f"🚀 Scanning {len(PAIRS)} pairs on {tf}...")
    
    for pair in PAIRS:
        df = get_data(pair, bars, tf)
        if df.empty:
            print(f"❌ {pair}: No data from Yahoo")
            continue
            
        df = calculate(df, rsi_len, ema_fast, ema_slow)
        if df.empty:
            print(f"⚠️ {pair}: Not enough bars for indicators")
            continue
            
        latest = df.iloc[-1]
        s = score(latest)
        results.append({
            "Pair": pair.replace("=X",""),
            "Score": s,
            "Trend": label(s),
            "RSI": round(float(latest["RSI"]), 2)
        })
        print(f"✅ {pair}: Scored {s}")
        time.sleep(0.1)

    if not results:
        print("Empty results - returning empty DataFrame")
        return pd.DataFrame(columns=["Pair", "Score", "Trend", "RSI"])

    return pd.DataFrame(results).sort_values(by="Score", ascending=False)

if __name__ == "__main__":
    # Test with 3mo to ensure we have enough history for the 200 EMA
    print(run_scanner("1d", "3mo", 14, 50, 200))