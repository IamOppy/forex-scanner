#app.py
import streamlit as st
import pandas as pd
import scanner
from scanner import run_scanner
import importlib
importlib.reload(scanner)
import time

st.set_page_config(layout="wide")
st.title("🔥 Forex Trend Scanner PRO")

# Sidebar
st.sidebar.header("⚙️ Settings")

timeframe = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
bars = st.sidebar.selectbox("History", ["1mo", "3mo", "1y"])
rsi_len = st.sidebar.slider("RSI Length", 5, 30, 14)
ema_fast = st.sidebar.slider("Fast EMA", 5, 100, 50)
ema_slow = st.sidebar.slider("Slow EMA", 50, 300, 200)

auto_refresh = st.sidebar.checkbox("Auto Refresh")
refresh_rate = st.sidebar.slider("Refresh (sec)", 10, 120, 30)

run = st.sidebar.button("Run Scanner")

placeholder = st.empty()

def color_row(val):
    if val >= 2:
        return "background-color: #00cc66"
    elif val <= -2:
        return "background-color: #ff4d4d"
    return ""

while run or auto_refresh:
    df = run_scanner(timeframe, bars, rsi_len, ema_fast, ema_slow)

    with placeholder.container():

        if df.empty:
            st.warning("⚠️ No data found. Try different settings.")
        else:
            st.success("Scan complete")

            # 🔥 Styled table
            st.subheader("📊 Market Overview")

            styled = df.style.map(color_row, subset=["Score"])
            st.dataframe(styled, use_container_width=True)

            # 📈 Chart
            st.subheader("📈 Trend Strength")
            st.bar_chart(df.set_index("Pair")["Score"])

            # 🔥 Top signals
            st.subheader("🔥 Best Setups")

            bullish = df[df["Score"] >= 2]
            bearish = df[df["Score"] <= -2]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🟢 Bullish")
                st.dataframe(bullish)

            with col2:
                st.markdown("### 🔴 Bearish")
                st.dataframe(bearish)

    if not auto_refresh:
        break

    time.sleep(refresh_rate)