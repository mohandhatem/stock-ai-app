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
# 1. إعدادات الصفحة والتصميم (أسود بالكامل زي Webull)
# ==========================================
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* خلفية سوداء بالكامل */
.stApp { background-color: #000000; color: #ffffff; }
.block-container { padding-top: 0.5rem; padding-bottom: 2rem; max-width: 100%; }

/* إخفاء الكيبورد في القائمة المنسدلة */
div[data-baseweb="select"] input { display: none !important; }

/* تنسيق الشريط العلوي */
.top-bar { display: flex; align-items: center; justify-content: space-between; padding: 5px 10px; font-family: sans-serif; margin-bottom: 5px;}
.ticker-name { font-size: 22px; font-weight: bold; color: #fff; }
.ohlc-data { color: #d1d4dc; font-weight: bold; font-size: 13px;}
.green-text { color: #00c853; }
.red-text { color: #ff3d00; }

/* تنسيق الكروت السفلية */
.side-card { background-color: #131722; border: 1px solid #2a2e39; border-radius: 8px; padding: 15px; margin-bottom: 15px;}
.live-card { border-left: 4px solid #00c853; }
.options-card { border-left: 4px solid #00bcd4; }
.general-card { border-left: 4px solid #ff9800; }
.card-title { color: #d1d4dc; font-size: 15px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #2a2e39; padding-bottom: 5px;}
.price-text { font-size: 26px; font-weight: bold; margin: 0; }
.pre-market-text { font-size: 13px; color: #ff9800; font-weight: bold; margin: 0; margin-top: 2px;}
.change-text { font-size: 14px; margin: 0; margin-bottom: 10px;}
.rec-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;}
.rec-label { color: #888; }
.news-item { font-size: 12px; margin-bottom: 8px; color: #d1d4dc; line-height: 1.4;}
.score-badge { font-size: 24px; font-weight: bold; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px;}
.points-details { font-size: 11px; color: #9ca3af; text-align: right; margin-top: 5px; line-height: 1.6; border-top: 1px dashed #2a2e39; padding-top: 8px; }

/* ثبيت الشارت في مكانه */
.stPlotlyChart { position: sticky; top: 0; z-index: 999; background-color: #000000; padding-bottom: 5px;}

</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, limit=None, key="live_refresh")

# ==========================================
# 2. البيانات والقوائم
# ==========================================
US_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", 
    "JPM", "V", "WMT", "DIS", "ORCL", "CRM", "ADBE", "AVGO", "QCOM", "BAC", 
    "GS", "MA", "PYPL", "COST", "NKE", "SBUX", "MCD", "JNJ", "UNH", "PFE", 
    "LLY", "XOM", "CVX", "BA", "PLTR", "IBM", "GE", "CAT", "MMM", "HON", 
    "UPS", "FDX", "T", "VZ", "TMUS", "CMCSA", "CSCO", "TXN", "AMAT", "MU", 
    "LRCX", "SBRC", "SHOP", "SQ", "ROKU", "ZM", "DOCU", "SNOW", "U", "RBLX", 
    "COIN", "HOOD", "SOFI", "AI", "PATH", "NET", "DDOG", "CRWD", "OKTA", "PANW"
]

INDICES = {
    "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", 
    "Russell 2000": "^RUT", "VIX (التقلب)": "^VIX", "TASI (تاسي)": "^TASI.SR"
}

COMPANY_NAMES = {
    "^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones", "^RUT": "Russell 2000", "^VIX": "VIX", "^TASI.SR": "TASI (تاسي)",
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "TSLA": "Tesla", 
    "NVDA": "NVIDIA", "META": "Meta", "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel", 
    "JPM": "JPMorgan", "V": "Visa", "WMT": "Walmart", "DIS": "Disney", "ORCL": "Oracle", 
    "CRM": "Salesforce", "ADBE": "Adobe", "AVGO": "Broadcom", "QCOM": "Qualcomm", "BAC": "Bank of America", 
    "GS": "Goldman Sachs", "MA": "Mastercard", "PYPL": "PayPal", "COST": "Costco", "NKE": "Nike", 
    "SBUX": "Starbucks", "MCD": "McDonald's", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "PFE": "Pfizer", 
    "LLY": "Eli Lilly", "XOM": "Exxon Mobil", "CVX": "Chevron", "BA": "Boeing", "PLTR": "Palantir", 
    "IBM": "IBM", "GE": "General Electric", "CAT": "Caterpillar", "MMM": "3M", "HON": "Honeywell",
    "UPS": "UPS", "FDX": "FedEx", "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobile",
    "CMCSA": "Comcast", "CSCO": "Cisco", "TXN": "Texas Instruments", "AMAT": "Applied Materials", "MU": "Micron",
    "LRCX": "Lam Research", "SBRC": "Sound Equity", "SHOP": "Shopify", "SQ": "Block (Square)", 
    "ROKU": "Roku", "ZM": "Zoom", "DOCU": "DocuSign", "SNOW": "Snowflake", "U": "Unity",
    "RBLX": "Roblox", "COIN": "Coinbase", "HOOD": "Robinhood", "SOFI": "SoFi", "AI": "C3.ai",
    "PATH": "UiPath", "NET": "Cloudflare", "DDOG": "Datadog", "CRWD": "CrowdStrike", "OKTA": "Okta", "PANW": "Palo Alto"
}

MARKETS = {
    "🇺🇸 أمريكي (US)": US_TICKERS,
    "📊 المؤشرات (Indices)": list(INDICES.keys())
}

TIMEFRAMES = {
    "1m": {"interval": "1m", "period": "7d"},
    "5m": {"interval": "5m", "period": "60d"},
    "15m": {"interval": "15m", "period": "60d"},
    "30m": {"interval": "30m", "period": "60d"},
    "1h": {"interval": "60m", "period": "730d"},
    "1d": {"interval": "1d", "period": "5y"}
}

# ==========================================
# 3. دوال جلب البيانات والتحليل
# ==========================================
@st.cache_data(ttl=60)
def fetch_data(ticker, interval, period):
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        if df.empty:
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_extended_hours(ticker):
    try:
        info = yf.Ticker(ticker).info
        pre = info.get('preMarketPrice')
        post = info.get('postMarketPrice')
        if pre: return pre, "PRE"
        if post: return post, "POST"
        return None, None
    except: return None, None

@st.cache_data(ttl=300)
def fetch_news(ticker):
    try:
        news = yf.Ticker(ticker).news
        return [n['title'] for n in news[:3]] if news else []
    except: return []

def analyze_stock(df, ticker):
    if df.empty or len(df) < 50: 
        return 50, False, False, "بيانات غير كافية", 0, 0, 0, "لا توجد بيانات"

    close, high, low, open_p, volume = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
    current_price = close.iloc[-1]
    prev_close = close.iloc[-2]
    atr = (high - low).rolling(14).mean().iloc[-1]

    sma20 = close.rolling(20).mean().iloc[-1]
    sma30 = close.rolling(30).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    
    is_above_mas = (current_price > sma20) and (sma20 > sma30) and (sma30 > sma50)
    is_below_mas = (current_price < sma20) and (sma20 < sma30) and (sma30 < sma50)

    score = 50
    breakdown = ["نقاط البداية: 50"]
    
    if is_above_mas:
        score += 15
        breakdown.append("فوق المتوسطات: +15")
    elif is_below_mas:
        score -= 15
        breakdown.append("تحت المتوسطات: -15")

    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    if 50 <= rsi < 70: 
        score += 10
        breakdown.append("RSI إيجابي: +10")
    elif rsi >= 70: 
        score -= 10
        breakdown.append("RSI تشبع شرائي: -10")
    elif rsi <= 30:
        score += 10
        breakdown.append("RSI تشبع بيعي: +10")

    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    signal = macd.ewm(span=9, adjust=False).mean()
    if macd.iloc[-1] > signal.iloc[-1]: 
        score += 10
        breakdown.append("MACD إيجابي: +10")
    else: 
        score -= 10
        breakdown.append("MACD سلبي: -10")

    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    stoch_d = stoch_k.rolling(window=3).mean()
    
    if stoch_k.iloc[-1] > stoch_d.iloc[-1] and stoch_k.iloc[-1] < 80:
        score += 5
        breakdown.append("Stochastic إيجابي: +5")
    elif stoch_k.iloc[-1] < stoch_d.iloc[-1] and stoch_k.iloc[-1] > 20:
        score -= 5
        breakdown.append("Stochastic سلبي: -5")

    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)

    if current_price <= bb_lower.iloc[-1]:
        score += 10
        breakdown.append("دعم بولينجر: +10")
    elif current_price >= bb_upper.iloc[-1]:
        score -= 10
        breakdown.append("مقاومة بولينجر: -10")

    if current_price >= high.tail(20).max() * 0.99: 
        score += 10
        breakdown.append("اختراق سعري: +10")
        
    if volume.iloc[-1] > volume.rolling(20).mean().iloc[-1] * 1.5:
        score += 10
        breakdown.append("انفجار سيولة: +10")

    score = max(10, min(95, score))
    breakdown.append(f"<b>الإجمالي: {score}%</b>")
    
    if score >= 65:
        rec = "شراء قوي (STRONG BUY)" if is_above_mas else "شراء (BUY)"
        intraday_target = current_price + (atr * 1.0)
        swing_target = current_price + (atr * 3.0)
        stop_loss = current_price - (atr * 1.5)
    elif score <= 40:
        rec = "بيع قوي (STRONG SELL)" if is_below_mas else "بيع (SELL)"
        intraday_target = current_price - (atr * 1.0)
        swing_target = current_price - (atr * 3.0)
        stop_loss = current_price + (atr * 1.5)
    else:
        rec = "احتفاظ (HOLD)"
        intraday_target = current_price
        swing_target = current_price
        stop_loss = current_price - (atr * 1.5)

    return score, is_above_mas, is_below_mas, rec, intraday_target, swing_target, stop_loss, "<br>".join(breakdown)

@st.cache_data(ttl=600)
def evaluate_tickers(tickers, interval, period):
    results = {}
    for t in tickers:
        try:
            df = fetch_data(t, interval, period)
            if len(df) < 50: continue
            score, is_above_mas, is_below_mas, rec, _, _, _, _ = analyze_stock(df, t)
            results[t] = {'score': score, 'is_above_mas': is_above_mas, 'is_below_mas': is_below_mas, 'rec': rec}
            time.sleep(0.2) 
        except: pass
    return results

# ==========================================
# 4. واجهة المستخدم (فوق وتحت)
# ==========================================

# --- 1. القوائم المنسدلة فوق خالص ---
c1, c2, c3 = st.columns([1.5, 1.5, 1])
with c1:
    market_options = list(MARKETS.keys())
    selected_market = st.selectbox("السوق", market_options, index=0, label_visibility="collapsed")
with c2:
    filter_mode = st.selectbox("الفلتر", ["الكل ⚖️", "إيجابي (فوق المتوسطات) 🚀", "سلبي (تحت المتوسطات) 🔻"], label_visibility="collapsed")
with c3:
    selected_timeframe = st.selectbox("الإطار", list(TIMEFRAMES.keys()), index=3, label_visibility="collapsed")

tf_config = TIMEFRAMES[selected_timeframe]

if selected_market == "📊 المؤشرات (Indices)":
    ticker_symbols = list(INDICES.values())
    custom_ticker = st.text_input("أو اكتب رمز المؤشر يدوياً (مثال: ^GSPC):", "").strip().upper()
else:
    ticker_symbols = US_TICKERS
    custom_ticker = st.text_input("أو اكتب رمز السهم يدوياً (مثال: AAPL, TSLA):", "").strip().upper()

with st.spinner(f"جاري تحديث البيانات بناءً على فريم {selected_timeframe}..."):
    eval_data = evaluate_tickers(ticker_symbols, tf_config["interval"], tf_config["period"])

if filter_mode == "إيجابي (فوق المتوسطات) 🚀":
    filtered_tickers = [t for t in ticker_symbols if eval_data.get(t, {}).get('is_above_mas', False)]
elif filter_mode == "سلبي (تحت المتوسطات) 🔻":
    filtered_tickers = [t for t in ticker_symbols if eval_data.get(t, {}).get('is_below_mas', False)]
else:
    filtered_tickers = ticker_symbols

if not filtered_tickers:
    st.warning(f"لا توجد أسهم تتطابق مع الفلتر المختار ({filter_mode}) على فريم {selected_timeframe}. تم عرض كل الأسهم بدلاً من ذلك.")
    filtered_tickers = ticker_symbols

filtered_tickers = sorted(filtered_tickers, key=lambda x: eval_data.get(x, {}).get('score', 0), reverse=True)

def format_ticker(t):
    data = eval_data.get(t, {'is_above_mas': False, 'is_below_mas': False, 'score': 50})
    if data.get('is_above_mas'): prefix = "🚀"
    elif data.get('is_below_mas'): prefix = "🔻"
    else: prefix = "⚖️"
    
    display_name = COMPANY_NAMES.get(t, t) 
    
    if display_name == t:
        return f"{prefix} {t} - {data.get('score', 50)}%"
    else:
        return f"{prefix} {display_name} ({t}) - {data.get('score', 50)}%"

# اختيار السهم
selected_ticker = st.selectbox("اختر السهم:", filtered_tickers, format_func=format_ticker, label_visibility="collapsed")
if custom_ticker:
    selected_ticker = custom_ticker

# --- 2. الشارت في النص (ثابت) ---
if selected_ticker:
    df = fetch_data(selected_ticker, tf_config["interval"], tf_config["period"])

    if not df.empty:
        current_price = df['Close'].iloc[-1].item()
        prev_close = df['Close'].iloc[-2].item()
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        color = "#00c853" if change >= 0 else "#ff3d00"
        sign = "+" if change >= 0 else ""

        pre_price, pre_type = fetch_extended_hours(selected_ticker)
        pre_html = f'<p class="pre-market-text">{pre_type}: ${pre_price:.2f}</p>' if pre_price else ""

        display_name_header = COMPANY_NAMES.get(selected_ticker, selected_ticker)
        
        st.markdown(f"""
        <div class="top-bar">
            <span class="ticker-name">{display_name_header} · {selected_ticker} · {selected_timeframe}</span>
            <span class="ohlc-data">C {current_price:.2f}</span>
            <span class="{'green-text' if change >= 0 else 'red-text'}" style="font-weight:bold;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</span>
        </div>
        """, unsafe_allow_html=True)

        df_plot = df.tail(100).copy()
        df_plot['SMA_20'] = df['Close'].rolling(window=20).mean().tail(100)
        df_plot['SMA_30'] = df['Close'].rolling(window=30).mean().tail(100)
        df_plot['SMA_50'] = df['Close'].rolling(window=50).mean().tail(100)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
        fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Price", increasing_line_color='#00c853', decreasing_line_color='#ff3d00'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#ff9800', width=1.2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_30'], mode='lines', name='SMA 30', line=dict(color='#2196f3', width=1.2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#9c27b0', width=1.2)), row=1, col=1)
        
        colors = ['#00c853' if close >= open else '#ff3d00' for open, close in zip(df_plot['Open'], df_plot['Close'])]
        fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], name="Volume", marker_color=colors), row=2, col=1)
        
        # خلفية سوداء بالكامل زي التطبيق
        fig.update_layout(
            template="plotly_dark", 
            paper_bgcolor='#000000', 
            plot_bgcolor='#000000', 
            height=350, # طول مناسب للموبايل
            autosize=True, 
            margin=dict(l=0, r=0, t=10, b=0), 
            showlegend=False, 
            dragmode="pan", 
            hovermode="x unified", 
            xaxis=dict(showgrid=True, gridcolor='#2a2e39', fixedrange=False),
            yaxis=dict(showgrid=True, gridcolor='#2a2e39', side='right', fixedrange=False)
        )
        fig.update_yaxes(showgrid=False, side='right', row=2, col=1, fixedrange=False)
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

    # --- 3. التحليلات والتوصيات تحت خالص ---
    if not df.empty:
        score, is_above_mas, is_below_mas, recommendation, intraday_t, swing_t, stock_sl, breakdown = analyze_stock(df, selected_ticker)
        
        if score >= 60: score_color = "#00c853"
        elif score <= 40: score_color = "#ff3d00"
        else: score_color = "#ff9800"

        st.markdown(f"""
        <div class="side-card live-card" style="border-left-color: {score_color};">
        <div class="card-title">🧠 محرك التحليل ({selected_timeframe})</div>
        <div class="score-badge" style="background-color: {score_color}20; color: {score_color}; border: 1px solid {score_color};">
            درجة الثقة: {score}%
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 16px; color: {score_color}; margin-bottom: 5px;">{recommendation}</div>
        
        <div class="points-details">
            <b>تفصيل النقاط:</b><br>
            {breakdown}
        </div>
        
        <div style="border-top: 1px solid #2a2e39; margin: 10px 0;"></div>
        <p class="price-text" style="color: {color};">${current_price:.2f}</p>
        {pre_html}
        <p class="change-text" style="color: {color}; margin-top: 5px;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</p>
        
        <div style="background: {score_color}15; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <div class="rec-item"><span class="rec-label">هدف الجلسة:</span> <span style="color:{score_color}; font-weight:bold;">${intraday_t:.2f}</span></div>
            <div class="rec-item"><span class="rec-label">هدف الانتهاء:</span> <span style="color:{score_color}; font-weight:bold;">${swing_t:.2f}</span></div>
            <div class="rec-item"><span class="rec-label">وقف الخسارة:</span> <span style="color:#ff3d00; font-weight:bold;">${stock_sl:.2f}</span></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        if selected_ticker.isalpha():
            try:
                stock = yf.Ticker(selected_ticker)
                if stock.options:
                    chain = stock.option_chain(stock.options[0])
                    calls, puts = chain.calls, chain.puts
                    if not calls.empty and not puts.empty:
                        chosen = calls.loc[abs(calls['strike'] - current_price).idxmin()] if "شراء" in recommendation else puts.loc[abs(puts['strike'] - current_price).idxmin()]
                        last_price = chosen['lastPrice']
                        if last_price > 0:
                            st.markdown(f"""
                            <div class="side-card options-card">
                            <div class="card-title">📄 عقود الخيارات</div>
                            <div class="rec-item"><span class="rec-label">النوع:</span> <span style="color:#00bcd4; font-weight:bold;">{"Call" if "شراء" in recommendation else "Put"}</span></div>
                            <div class="rec-item"><span class="rec-label">الانتهاء:</span> <span>{stock.options[0]}</span></div>
                            <div class="rec-item"><span class="rec-label">Strike:</span> <span>${chosen['strike']:.2f}</span></div>
                            <div class="rec-item"><span class="rec-label">سعر العقد:</span> <span style="color:#fff; font-weight:bold;">${last_price:.2f}</span></div>
                            <div style="border-top: 1px dashed #2a2e39; margin: 8px 0;"></div>
                            <div class="rec-item"><span class="rec-label">هدف الجلسة (+30%):</span> <span style="color:#00c853; font-weight:bold;">${last_price * 1.30:.2f}</span></div>
                            <div class="rec-item"><span class="rec-label">هدف الانتهاء (+100%):</span> <span style="color:#00c853; font-weight:bold;">${last_price * 2.00:.2f}</span></div>
                            <div class="rec-item"><span class="rec-label">وقف الخسارة (-20%):</span> <span style="color:#ff3d00; font-weight:bold;">${last_price * 0.80:.2f}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
            except:
                pass

        news = fetch_news(selected_ticker)
        news_html = "".join([f"<div class='news-item'>• {n}</div>" for n in news]) if news else "<div class='news-item'>لا توجد أخبار حديثة.</div>"
        st.markdown(f"""
        <div class="side-card general-card">
        <div class="card-title">📰 أخبار السهم</div>
        {news_html}
        </div>
        """, unsafe_allow_html=True)
