import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
import datetime
import time

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp { background-color: #131722; color: #d1d4dc; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
.top-bar { display: flex; align-items: center; gap: 15px; padding: 5px 10px; font-family: sans-serif; margin-bottom: 5px;}
.ticker-name { font-size: 20px; font-weight: bold; color: #fff; }
.ohlc-data { color: #d1d4dc; font-weight: bold; font-size: 14px;}
.green-text { color: #089981; }
.red-text { color: #f23645; }
.side-card { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; padding: 15px; margin-bottom: 15px;}
.live-card { border-left: 4px solid #ff9800; }
.options-card { border-left: 4px solid #00bcd4; }
.liquidity-card { border-left: 4px solid #e91e63; }
.general-card { border-left: 4px solid #00c853; }
.card-title { color: #d1d4dc; font-size: 14px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #2a2e39; padding-bottom: 5px;}
.price-text { font-size: 22px; font-weight: bold; margin: 0; }
.pre-market-text { font-size: 13px; color: #ff9800; font-weight: bold; margin: 0; margin-top: 2px;}
.change-text { font-size: 13px; margin: 0; margin-bottom: 10px;}
.rec-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;}
.rec-label { color: #888; }
.news-item { font-size: 12px; margin-bottom: 8px; color: #d1d4dc; line-height: 1.4;}
.score-badge { font-size: 24px; font-weight: bold; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;}
.breakdown-text { font-size: 10px; color: #6c757d; text-align: center; margin-top: 5px; line-height: 1.5; border-top: 1px dashed #2a2e39; padding-top: 5px;}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, limit=None, key="live_refresh")

# ==========================================
# 2. البيانات والدوال الأساسية
# ==========================================
COMPANY_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", 
    "TSLA": "Tesla", "NVDA": "NVIDIA", "META": "Meta", "NFLX": "Netflix", 
    "AMD": "AMD", "INTC": "Intel", "JPM": "JPMorgan", "V": "Visa", "WMT": "Walmart", "DIS": "Disney",
    "ORCL": "Oracle", "CRM": "Salesforce", "ADBE": "Adobe", "AVGO": "Broadcom", "QCOM": "Qualcomm",
    "BAC": "Bank of America", "GS": "Goldman Sachs", "MA": "Mastercard", "PYPL": "PayPal",
    "COST": "Costco", "NKE": "Nike", "SBUX": "Starbucks", "MCD": "McDonald's",
    "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "PFE": "Pfizer", "LLY": "Eli Lilly",
    "XOM": "Exxon Mobil", "CVX": "Chevron", "BA": "Boeing", "PLTR": "Palantir",
    
    "2222.SR": "أرامكو", "2010.SR": "سابك", "1120.SR": "الراجحي", "1180.SR": "الأهلي", 
    "2350.SR": "كيان", "1211.SR": "معادن", "4013.SR": "دله الصحية", "7010.SR": "الاتصالات",
    "4300.SR": "دار الأركان", "2280.SR": "المراعي", "7020.SR": "موبايلي", "7030.SR": "زين",
    "4014.SR": "علم", "1111.SR": "تداول", "4015.SR": "الدوائية", "4002.SR": "المواساة",
    "4004.SR": "الحبيب", "4161.SR": "بن داود", "4192.SR": "لجام", "7203.SR": "طيران ناس",
    "2082.SR": "أكوا باور", "6018.SR": "نادك", "4191.SR": "أم القرى", "8230.SR": "الراجحي للتأمين",
    
    "COMI.CA": "البنك التجاري", "EFIH.CA": "إي فاينانس", "HRHO.CA": "هيرميس", "ETEL.CA": "المصرية للاتصالات", 
    "SWDY.CA": "السويدي", "EAST.CA": "الشرقية إيسترن", "TMGH.CA": "طلعت مصطفى", "ABUK.CA": "أبو قير", "SKPC.CA": "سيدي كرير", "ORAS.CA": "أوراسكوم",
}

MARKETS = {
    "🇺🇸 أمريكي (US)": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", "JPM", "V", "WMT", "DIS",
        "ORCL", "CRM", "ADBE", "AVGO", "QCOM", "BAC", "GS", "MA", "PYPL", "COST", "NKE", "SBUX", "MCD", 
        "JNJ", "UNH", "PFE", "LLY", "XOM", "CVX", "BA", "PLTR"
    ],
    "🇸🇦 سعودي (Tadawul)": [
        "2222.SR", "2010.SR", "1120.SR", "1180.SR", "2350.SR", "1211.SR", "4013.SR", "7010.SR", "4300.SR",
        "2280.SR", "7020.SR", "7030.SR", "4014.SR", "1111.SR", "4015.SR", "4002.SR", "4004.SR", "4161.SR",
        "4192.SR", "7203.SR", "2082.SR", "6018.SR", "4191.SR", "8230.SR"
    ],
    "🇪🇬 مصري (EGX)": ["COMI.CA", "EFIH.CA", "HRHO.CA", "ETEL.CA", "SWDY.CA", "EAST.CA", "TMGH.CA", "ABUK.CA", "SKPC.CA", "ORAS.CA"],
}

INDICES = {
    "📈 S&P 500": "^GSPC", "📈 Dow Jones": "^DJI", "📈 NASDAQ": "^IXIC", 
    "📈 TASI (تاسي)": "^TASI.SR", "📈 EGX 30": "^EGX30.CA",
    "💱 USD/EGP": "EGP=X", "💱 USD/SAR": "SAR=X",
}

TIMEFRAMES = {
    "1m": {"interval": "1m", "period": "7d"}, "5m": {"interval": "5m", "period": "60d"},
    "15m": {"interval": "15m", "period": "60d"}, "1h": {"interval": "60m", "period": "730d"},
    "1d": {"interval": "1d", "period": "5y"}, "1wk": {"interval": "1wk", "period": "5y"},
}

@st.cache_data(ttl=60)
def fetch_data(ticker, interval, period):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_extended_hours(ticker):
    try:
        info = yf.Ticker(ticker).info
        price = info.get('preMarketPrice') or info.get('postMarketPrice') or info.get('regularMarketPreviousClose')
        return price
    except: return None

@st.cache_data(ttl=300)
def get_liquidity_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        vol = info.get('averageVolume', 0)
        bid = info.get('bid', 0)
        ask = info.get('ask', 0)
        price = info.get('currentPrice', info.get('regularMarketPrice', 1))
        spread_pct = ((ask - bid) / price) * 100 if bid > 0 and ask > 0 and price > 0 else 0
        if vol > 5_000_000 and spread_pct < 0.1: status, color = "عالية جداً", "#00c853"
        elif vol > 1_000_000: status, color = "متوسطة", "#ff9800"
        else: status, color = "ضعيفة", "#ff3d00"
        return status, spread_pct, color
    except: return "غير متاح", 0.0, "#888"

@st.cache_data(ttl=300)
def fetch_news(ticker):
    try:
        news = yf.Ticker(ticker).news
        return [n['title'] for n in news[:2]] if news else []
    except: return []

@st.cache_data(ttl=600)
def get_multi_factor_score(ticker):
    df = fetch_data(ticker, "1d", "1y")
    if df.empty or len(df) < 50: 
        return 50, "بيانات غير كافية", "محايد", 0, 0, 0, "لا توجد بيانات كافية"

    score = 50
    reasons = []
    p_trend, p_mom, p_vol, p_obv, p_candle = 0, 0, 0, 0, 0
    
    close, high, low, volume = df['Close'], df['High'], df['Low'], df['Volume']
    current_price = close.iloc[-1]
    atr = (high - low).rolling(14).mean().iloc[-1]

    try:
        sma20, sma50, sma200 = close.rolling(20).mean().iloc[-1], close.rolling(50).mean().iloc[-1], close.rolling(200).mean().iloc[-1] if len(close) >= 200 else close.rolling(50).mean().iloc[-1]
        if current_price > sma20 > sma50 > sma200: p_trend += 15; reasons.append("اتجاه صاعد قوي")
        elif current_price < sma20 < sma50 < sma200: p_trend -= 15; reasons.append("اتجاه هابط قوي")
        elif current_price > sma50: p_trend += 10; reasons.append("اتجاه صاعد")
        elif current_price < sma50: p_trend -= 10; reasons.append("اتجاه هابط")
    except: pass

    try:
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        if 60 <= rsi < 70: p_mom += 5; reasons.append("زخم إيجابي")
        elif 30 < rsi <= 40: p_mom -= 5; reasons.append("زخم سلبي")
        elif rsi <= 30: p_mom += 3; reasons.append("تشبع بيعي")
        
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        if macd.iloc[-1] > signal.iloc[-1]: p_mom += 5; reasons.append("MACD إيجابي")
        else: p_mom -= 5; reasons.append("MACD سلبي")
    except: pass

    try:
        upper_band = close.rolling(20).mean() + (close.rolling(20).std() * 2)
        lower_band = close.rolling(20).mean() - (close.rolling(20).std() * 2)
        if current_price >= upper_band.iloc[-1]: p_vol -= 5; reasons.append("مقاومة بولينجر")
        elif current_price <= lower_band.iloc[-1]: p_vol += 5; reasons.append("دعم بولينجر")
    except: pass

    try:
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        if obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]: p_obv += 5; reasons.append("تدفق أموال إيجابي")
        else: p_obv -= 5; reasons.append("تدفق أموال سلبي")
    except: pass

    try:
        last_open, last_close = df['Open'].iloc[-1], df['Close'].iloc[-1]
        prev_open, prev_close = df['Open'].iloc[-2], df['Close'].iloc[-2]
        if prev_close < prev_open and last_close > last_open and last_close > prev_open and last_open < prev_close:
            p_candle += 10; reasons.append("ابتلاع صاعد")
        elif prev_close > prev_open and last_close < last_open and last_close < prev_open and last_open > prev_close:
            p_candle -= 10; reasons.append("ابتلاع هابط")
    except: pass

    score += (p_trend + p_mom + p_vol + p_obv + p_candle)
    score = max(0, min(100, score))
    breakdown_str = f"الاتجاه: {p_trend:+} | الزخم: {p_mom:+} | التقلب: {p_vol:+} | الفوليوم: {p_obv:+} | الشموع: {p_candle:+}"
    
    if score >= 60:
        rec = "شراء (BUY)"
        intraday_target = current_price + (atr * 0.5)
        swing_target = current_price + (atr * 2.0)
        stop_loss = current_price - (atr * 1.5)
    elif score <= 40:
        rec = "بيع (SELL)"
        intraday_target = current_price - (atr * 0.5)
        swing_target = current_price - (atr * 2.0)
        stop_loss = current_price + (atr * 1.5)
    else:
        rec = "احتفاظ (HOLD)"
        intraday_target = current_price
        swing_target = current_price
        stop_loss = current_price - (atr * 1.0)

    return score, rec, " | ".join(reasons[:2]), intraday_target, swing_target, stop_loss, breakdown_str

@st.cache_data(ttl=600)
def get_options_recommendation(ticker, current_price, general_rec):
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        if not expirations: return None
        
        valid_exps = [e for e in expirations if (datetime.datetime.strptime(e, '%Y-%m-%d').date() - datetime.date.today()).days > 14]
        if not valid_exps: valid_exps = expirations
        target_exp = valid_exps[0]
        
        chain = stock.option_chain(target_exp)
        calls, puts = chain.calls, chain.puts
        if calls.empty or puts.empty: return None
        
        chosen = calls.loc[abs(calls['strike'] - current_price).idxmin()] if "شراء" in general_rec else puts.loc[abs(puts['strike'] - current_price).idxmin()]
        option_type = "Call (ATM)" if "شراء" in general_rec else "Put (ATM)"
            
        last_price = chosen['lastPrice']
        
        return {
            "type": option_type, "expiration": target_exp, "strike": chosen['strike'],
            "last_price": last_price, "stop_loss": last_price * 0.80, 
            "session_target": last_price * 1.30, 
            "expiry_target": last_price * 2.00,  
            "change": chosen.get('change', 0)
        }
    except: return None

# ==========================================
# 3. تقسيم الشاشة
# ==========================================
col_chart, col_sidebar = st.columns([3.5, 1.2], gap="medium")

with col_sidebar:
    st.markdown("### 📋 Watchlist")
    
    market_options = list(MARKETS.keys()) + ["📊 المؤشرات (Indices)"]
    selected_market = st.selectbox("السوق", market_options, index=0, label_visibility="collapsed")
    
    if selected_market == "📊 المؤشرات (Indices)":
        ticker_options = list(INDICES.keys())
        selected_ticker_display = st.selectbox("المؤشر", ticker_options, index=0, label_visibility="collapsed")
        selected_ticker = INDICES[selected_ticker_display]
    else:
        ticker_symbols = MARKETS[selected_market]
        
        stock_scores_dict = {}
        with st.spinner("جاري تقييم وترتيب الأسهم..."):
            for t in ticker_symbols:
                time.sleep(0.05) 
                s, _, _, _, _, _, _ = get_multi_factor_score(t)
                stock_scores_dict[t] = s
        
        # 🌟 الترتيب من الأكبر للأصغر
        sorted_tickers = sorted(ticker_symbols, key=lambda x: stock_scores_dict.get(x, 0), reverse=True)
        
        def format_ticker(t):
            s = stock_scores_dict.get(t, 50)
            name = COMPANY_NAMES.get(t, t)
            if s >= 60: emoji = "🟢"
            elif s <= 40: emoji = "🔴"
            else: emoji = "🟡"
            return f"{emoji} {name} ({t}) - {s}"
        
        # 🌟 عرض القائمة المرتبة
        selected_ticker = st.selectbox(
            "اختر السهم للتحليل التفصيلي:", 
            sorted_tickers, 
            format_func=format_ticker, 
            label_visibility="collapsed"
        )

    selected_timeframe = st.selectbox("الإطار الزمني", list(TIMEFRAMES.keys()), index=1, label_visibility="collapsed")
    
    tf_config = TIMEFRAMES[selected_timeframe]
    df = fetch_data(selected_ticker, tf_config["interval"], tf_config["period"])
    
    if not df.empty:
        current_price = df['Close'].iloc[-1].item()
        prev_close = df['Close'].iloc[-2].item()
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        ext_price = fetch_extended_hours(selected_ticker)
        ext_html = f'<p class="pre-market-text">PRE: ${ext_price:.2f}</p>' if ext_price and ext_price > 0 else ""

        color = "#00c853" if change >= 0 else "#ff3d00"
        sign = "+" if change >= 0 else ""

        total_score, recommendation, reasons, intraday_t, swing_t, stock_sl, breakdown = get_multi_factor_score(selected_ticker)
        score_color = "#00c853" if total_score >= 60 else ("#ff3d00" if total_score <= 40 else "#ff9800")
        
        st.markdown(f"""
        <div class="side-card live-card">
        <div class="card-title">🧠 محرك التقييم المتعدد</div>
        <div class="score-badge" style="background-color: {score_color}20; color: {score_color}; border: 1px solid {score_color};">{total_score} / 100</div>
        <div style="text-align: center; font-weight: bold; font-size: 16px; color: {score_color}; margin-bottom: 5px;">{recommendation}</div>
        <div style="font-size: 11px; color: #888; text-align: center; margin-bottom: 5px;">{reasons}</div>
        <div class="breakdown-text">{breakdown}</div>
        <div style="border-top: 1px solid #2a2e39; margin: 10px 0;"></div>
        
        <p class="price-text" style="color: {color};">${current_price:.2f}</p>
        {ext_html}
        <p class="change-text" style="color: {color}; margin-top: 5px;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</p>
        
        <div style="background: {score_color}15; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <div class="rec-item" style="margin-bottom: 5px;">
                <span class="rec-label" style="color: #ddd;">هدف الجلسة:</span> 
                <span style="color:{score_color}; font-weight:bold;">${intraday_t:.2f}</span>
            </div>
            <div class="rec-item" style="margin-bottom: 5px;">
                <span class="rec-label" style="color: #ddd;">هدف الانتهاء:</span> 
                <span style="color:{score_color}; font-weight:bold;">${swing_t:.2f}</span>
            </div>
            <div class="rec-item" style="margin-bottom: 0px;">
                <span class="rec-label" style="color: #ddd;">وقف الخسارة:</span> 
                <span style="color:#ff3d00; font-weight:bold;">${stock_sl:.2f}</span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        liq_status, spread, liq_color = get_liquidity_info(selected_ticker)
        st.markdown(f"""
        <div class="side-card liquidity-card">
        <div class="card-title">💧 تحليل السيولة (Liquidity)</div>
        <div class="rec-item"><span class="rec-label">حالة السيولة:</span> <span style="color:{liq_color}; font-weight:bold;">{liq_status}</span></div>
        <div class="rec-item"><span class="rec-label">فرق السعر (Spread):</span> <span>{spread:.2f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

        options_rec = get_options_recommendation(selected_ticker, current_price, recommendation)
        if options_rec:
            opt_color = "#00c853" if options_rec['change'] >= 0 else "#ff3d00"
            opt_sign = "+" if options_rec['change'] >= 0 else ""
            
            st.markdown(f"""
            <div class="side-card options-card">
            <div class="card-title">📄 توصية عقود الخيارات</div>
            <div class="rec-item"><span class="rec-label">النوع:</span> <span style="color:#00bcd4; font-weight:bold;">{options_rec['type']}</span></div>
            <div class="rec-item"><span class="rec-label">الانتهاء:</span> <span>{options_rec['expiration']}</span></div>
            <div class="rec-item"><span class="rec-label">Strike:</span> <span>${options_rec['strike']:.2f}</span></div>
            <div class="rec-item"><span class="rec-label">سعر العقد:</span> <span style="color:{opt_color}; font-weight:bold;">${options_rec['last_price']:.2f} ({opt_sign}{options_rec['change']:.2f})</span></div>
            <div style="border-top: 1px dashed #2a2e39; margin: 8px 0;"></div>
            <div class="rec-item"><span class="rec-label">هدف الجلسة (+30%):</span> <span style="color:#00c853; font-weight:bold;">${options_rec['session_target']:.2f}</span></div>
            <div class="rec-item"><span class="rec-label">هدف الانتهاء (+100%):</span> <span style="color:#00c853; font-weight:bold;">${options_rec['expiry_target']:.2f}</span></div>
            <div class="rec-item"><span class="rec-label">وقف الخسارة:</span> <span style="color:#ff3d00; font-weight:bold;">${options_rec['stop_loss']:.2f}</span></div>
            </div>
            """, unsafe_allow_html=True)

        news = fetch_news(selected_ticker)
        news_html = "".join([f"<div class='news-item'>• {n}</div>" for n in news]) if news else "<div class='news-item'>لا توجد أخبار حديثة.</div>"
        st.markdown(f"""
        <div class="side-card general-card">
        <div class="card-title">📰 أخبار السهم</div>
        {news_html}
        </div>
        """, unsafe_allow_html=True)

with col_chart:
    if not df.empty:
        company_name = COMPANY_NAMES.get(selected_ticker, selected_ticker)
        st.markdown(f"""
        <div class="top-bar">
            <span class="ticker-name">{company_name} · {selected_ticker} · {selected_timeframe}</span>
            <span class="ohlc-data">O {df['Open'].iloc[-1]:.2f}</span>
            <span class="ohlc-data">H {df['High'].iloc[-1]:.2f}</span>
            <span class="ohlc-data">L {df['Low'].iloc[-1]:.2f}</span>
            <span class="ohlc-data">C {current_price:.2f}</span>
            <span class="{'green-text' if change >= 0 else 'red-text'}" style="font-weight:bold;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</span>
        </div>
        """, unsafe_allow_html=True)

        df_plot = df.tail(100).copy()
        df_plot['SMA_20'] = df['Close'].rolling(window=20).mean().tail(100)
        df_plot['SMA_50'] = df['Close'].rolling(window=50).mean().tail(100)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
        
        fig.add_trace(go.Candlestick(
            x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Price",
            increasing_line_color='#089981', decreasing_line_color='#f23645'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#ff9800', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#9c27b0', width=1.5)), row=1, col=1)
        
        colors = ['#089981' if close >= open else '#f23645' for open, close in zip(df_plot['Open'], df_plot['Close'])]
        fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], name="Volume", marker_color=colors), row=2, col=1)

        fig.update_layout(
            template="plotly_dark", paper_bgcolor='#131722', plot_bgcolor='#131722', 
            height=700, width=1200, margin=dict(l=10, r=10, t=10, b=10), 
            showlegend=False, dragmode="pan", hovermode="x unified", uirevision='constant',
            xaxis=dict(showgrid=True, gridcolor='#2a2e39', fixedrange=False),
            yaxis=dict(showgrid=True, gridcolor='#2a2e39', side='right', fixedrange=False)
        )
        fig.update_yaxes(showgrid=False, side='right', row=2, col=1, fixedrange=False)

        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False, 'scrollZoom': True})