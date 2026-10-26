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
.block-container { padding-top: 0.5rem; padding-bottom: 1rem; max-width: 98%; }

.top-bar { display: flex; align-items: center; gap: 10px; padding: 5px; font-family: sans-serif; margin-bottom: 5px; flex-wrap: wrap;}
.ticker-name { font-size: 18px; font-weight: bold; color: #fff; }
.ohlc-data { color: #d1d4dc; font-weight: bold; font-size: 12px;}
.green-text { color: #089981; }
.red-text { color: #f23645; }

.side-card { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; padding: 12px; margin-bottom: 12px;}
.live-card { border-left: 4px solid #00c853; }
.options-card { border-left: 4px solid #00bcd4; }
.card-title { color: #d1d4dc; font-size: 13px; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #2a2e39; padding-bottom: 5px;}
.price-text { font-size: 20px; font-weight: bold; margin: 0; }
.change-text { font-size: 12px; margin: 0; margin-bottom: 8px;}
.rec-item { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px;}
.rec-label { color: #888; }
.news-item { font-size: 11px; margin-bottom: 6px; color: #d1d4dc; line-height: 1.4;}
.score-badge { font-size: 22px; font-weight: bold; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 5px;}
.points-details { font-size: 10px; color: #9ca3af; text-align: right; margin-top: 5px; line-height: 1.6; border-top: 1px dashed #2a2e39; padding-top: 8px; }

@media (max-width: 768px) {
    .block-container { padding: 0rem !important; }
    .side-card { border-radius: 0; margin-bottom: 5px; border-left: none; border-bottom: 2px solid #2a2e39; }
    .top-bar { padding: 2px; }
    .ticker-name { font-size: 16px; }
}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, limit=None, key="live_refresh")

# ==========================================
# 2. القوائم والأسماء
# ==========================================
SAUDI_TICKERS = ["2222.SR", "2010.SR", "1120.SR", "1180.SR", "2350.SR", "1211.SR", "4013.SR", "7010.SR", "4300.SR", "2280.SR", "7020.SR", "7030.SR", "4014.SR", "1111.SR", "4015.SR", "4002.SR", "4004.SR", "4161.SR", "4192.SR", "7203.SR", "2082.SR", "6018.SR", "4191.SR", "8230.SR", "1810.SR", "1322.SR", "4230.SR", "4001.SR", "2050.SR", "2170.SR", "2310.SR", "2380.SR", "2060.SR", "3020.SR", "4030.SR", "4200.SR", "4260.SR", "4342.SR", "4344.SR", "8010.SR", "8210.SR", "8300.SR", "4003.SR", "2320.SR", "6050.SR", "2083.SR", "4334.SR", "2230.SR", "4328.SR", "6016.SR", "4290.SR"]
US_TICKERS = ["SBRC", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", "JPM", "V", "WMT", "DIS", "ORCL", "CRM", "ADBE", "AVGO", "QCOM", "BAC", "GS", "MA", "PYPL", "COST", "NKE", "SBUX", "MCD", "JNJ", "UNH", "PFE", "LLY", "XOM", "CVX", "BA", "PLTR", "IBM", "GE", "CAT", "MMM", "HON", "UPS", "FDX", "T", "VZ", "TMUS", "CMCSA", "CSCO", "TXN", "AMAT", "MU", "LRCX"]
EGYPT_TICKERS = ["COMI.CA", "EFIH.CA", "HRHO.CA", "ETEL.CA", "SWDY.CA", "EAST.CA", "TMGH.CA", "ABUK.CA", "SKPC.CA", "ORAS.CA", "AMOC.CA", "ESRS.CA", "HELI.CA", "ORTE.CA", "PHDC.CA", "MNHD.CA"]

COMPANY_NAMES = {
    "SBRC": "Sound Equity", "2222.SR": "أرامكو", "2010.SR": "سابك", "1120.SR": "الراجحي", "1180.SR": "الأهلي", "2350.SR": "كيان", "1211.SR": "معادن", "4013.SR": "دله الصحية", "7010.SR": "الاتصالات", "4300.SR": "دار الأركان", "2280.SR": "المراعي", "7020.SR": "موبايلي", "7030.SR": "زين", "4014.SR": "علم", "1111.SR": "تداول", "4015.SR": "الدوائية", "4002.SR": "المواساة", "4004.SR": "الحبيب", "4161.SR": "بن داود", "4192.SR": "لجام", "7203.SR": "طيران ناس", "2082.SR": "أكوا باور", "6018.SR": "نادك", "4191.SR": "أم القرى", "8230.SR": "الراجحي للتأمين", "1810.SR": "سيرا القابضة", "1322.SR": "أملاك العالمية", "4230.SR": "البحر الأحمر", "4001.SR": "أسواق ع العثيم", "2050.SR": "صافولا", "2170.SR": "الأبحاث والإعلام", "2310.SR": "سبكيم", "2380.SR": "بترو رابغ", "2060.SR": "التصنيع", "3020.SR": "أسمنت اليمامة", "4030.SR": "البحري", "4200.SR": "الدريس", "4260.SR": "المواساة", "4342.SR": "جدوى ريت", "4344.SR": "الرياض ريت", "8010.SR": "التعاونية", "8210.SR": "بوبا العربية", "8300.SR": "الوطنية", "4003.SR": "الإنماء", "2320.SR": "البابطين", "6050.SR": "الأسماك", "2083.SR": "مرافق", "4334.SR": "المعذر ريت", "2230.SR": "الكيميائية", "4328.SR": "لدن", "6016.SR": "برغراينز", "4290.SR": "الخليج للتدريب",
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "TSLA": "Tesla", "NVDA": "NVIDIA", "META": "Meta", "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel", "JPM": "JPMorgan", "V": "Visa", "WMT": "Walmart", "DIS": "Disney", "ORCL": "Oracle", "CRM": "Salesforce", "ADBE": "Adobe", "AVGO": "Broadcom", "QCOM": "Qualcomm", "BAC": "Bank of America", "GS": "Goldman Sachs", "MA": "Mastercard", "PYPL": "PayPal", "COST": "Costco", "NKE": "Nike", "SBUX": "Starbucks", "MCD": "McDonald's", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "PFE": "Pfizer", "LLY": "Eli Lilly", "XOM": "Exxon Mobil", "CVX": "Chevron", "BA": "Boeing", "PLTR": "Palantir", "IBM": "IBM", "GE": "General Electric", "CAT": "Caterpillar",
    "COMI.CA": "البنك التجاري", "EFIH.CA": "إي فاينانس", "HRHO.CA": "هيرميس", "ETEL.CA": "المصرية للاتصالات", "SWDY.CA": "السويدي", "EAST.CA": "الشرقية إيسترن", "TMGH.CA": "طلعت مصطفى", "ABUK.CA": "أبو قير", "SKPC.CA": "سيدي كرير", "ORAS.CA": "أوراسكوم"
}

MARKETS = {"🇸🇦 سعودي (Tadawul)": SAUDI_TICKERS, "🇺🇸 أمريكي (US)": US_TICKERS, "🇪🇬 مصري (EGX)": EGYPT_TICKERS}

# تحديث الفريمات
TIMEFRAMES = {
    "1m": {"interval": "1m", "period": "7d"},
    "5m": {"interval": "5m", "period": "60d"},
    "15m": {"interval": "15m", "period": "60d"},
    "30m": {"interval": "30m", "period": "60d"},
    "1h": {"interval": "60m", "period": "730d"},
    "1d": {"interval": "1d", "period": "5y"}
}

# ==========================================
# 3. دوال التحليل
# ==========================================
@st.cache_data(ttl=60) # قللنا الكاش لـ دقيقة عشان البيانات تتحدث أسرع
def fetch_data(ticker, interval, period):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_news(ticker):
    try:
        news = yf.Ticker(ticker).news
        return [n['title'] for n in news[:2]] if news else []
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
        score += 20
        breakdown.append("فوق متوسط 20/30/50: +20")
    elif is_below_mas:
        score -= 20
        breakdown.append("تحت متوسط 20/30/50: -20")

    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    if 50 <= rsi < 70: 
        score += 10
        breakdown.append("زخم RSI: +10")
    elif rsi >= 70: 
        score -= 5
        breakdown.append("تشبع شرائي: -5")
    elif rsi <= 30:
        score += 5
        breakdown.append("تشبع بيعي: +5")

    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    signal = macd.ewm(span=9, adjust=False).mean()
    if macd.iloc[-1] > signal.iloc[-1]: 
        score += 10
        breakdown.append("MACD إيجابي: +10")
    else: 
        score -= 10
        breakdown.append("MACD سلبي: -10")

    recent_high = high.tail(20).max()
    if current_price >= recent_high * 0.99: 
        score += 10
        breakdown.append("اختراق سعري: +10")
        
    avg_vol = volume.rolling(20).mean().iloc[-1]
    if volume.iloc[-1] > avg_vol * 1.5:
        score += 10
        breakdown.append("انفجار سيولة: +10")

    score = max(10, min(95, score))
    breakdown.append(f"<b>الإجمالي: {score}%</b>")
    
    if score >= 70 and is_above_mas:
        rec = "شراء قوي (STRONG BUY)"
        intraday_target = current_price + (atr * 1.0)
        swing_target = current_price + (atr * 3.0)
        stop_loss = current_price - (atr * 1.5)
    elif score >= 55 and is_above_mas:
        rec = "شراء (BUY)"
        intraday_target = current_price + (atr * 0.5)
        swing_target = current_price + (atr * 2.0)
        stop_loss = current_price - (atr * 1.5)
    elif score <= 30 and is_below_mas:
        rec = "بيع قوي (STRONG SELL)"
        intraday_target = current_price - (atr * 1.0)
        swing_target = current_price - (atr * 3.0)
        stop_loss = current_price + (atr * 1.5)
    elif score <= 45 and is_below_mas:
        rec = "بيع (SELL)"
        intraday_target = current_price - (atr * 0.5)
        swing_target = current_price - (atr * 2.0)
        stop_loss = current_price + (atr * 1.5)
    else:
        rec = "احتفاظ (HOLD)"
        intraday_target = current_price
        swing_target = current_price
        stop_loss = current_price - (atr * 1.5)

    return score, is_above_mas, is_below_mas, rec, intraday_target, swing_target, stop_loss, "<br>".join(breakdown)

@st.cache_data(ttl=600)
def evaluate_tickers(tickers):
    results = {}
    for t in tickers:
        try:
            df = fetch_data(t, "1d", "1y")
            if len(df) < 50: continue
            score, is_above_mas, is_below_mas, rec, _, _, _, _ = analyze_stock(df, t)
            results[t] = {'score': score, 'is_above_mas': is_above_mas, 'is_below_mas': is_below_mas, 'rec': rec}
            time.sleep(0.1)
        except: pass
    return results

# ==========================================
# 4. واجهة المستخدم
# ==========================================
col_chart, col_sidebar = st.columns([2.5, 1], gap="medium")

with col_chart:
    c1, c2, c3 = st.columns([1.5, 1.5, 1])
    with c1:
        market_options = list(MARKETS.keys())
        selected_market = st.selectbox("السوق", market_options, index=1, label_visibility="collapsed")
    with c2:
        filter_mode = st.selectbox("الفلتر", ["الكل ⚖️", "إيجابي (فوق المتوسطات) 🚀", "سلبي (تحت المتوسطات) 🔻"], label_visibility="collapsed")
    with c3:
        selected_timeframe = st.selectbox("الإطار", list(TIMEFRAMES.keys()), index=0, label_visibility="collapsed")

    tickers_list = MARKETS[selected_market]
    
    with st.spinner("جاري فلترة وتحليل الأسهم..."):
        eval_data = evaluate_tickers(tickers_list)

    if filter_mode == "إيجابي (فوق المتوسطات) 🚀":
        filtered_tickers = [t for t, data in eval_data.items() if data['is_above_mas']]
    elif filter_mode == "سلبي (تحت المتوسطات) 🔻":
        filtered_tickers = [t for t, data in eval_data.items() if data['is_below_mas']]
    else:
        filtered_tickers = list(eval_data.keys())

    filtered_tickers = sorted(filtered_tickers, key=lambda x: eval_data[x]['score'], reverse=True)

    if not filtered_tickers:
        st.warning(f"لا توجد أسهم تتطابق مع الفلتر المختار ({filter_mode}) حالياً.")
        st.stop()

    def format_ticker(t):
        data = eval_data[t]
        if data['is_above_mas']: prefix = "🚀"
        elif data['is_below_mas']: prefix = "🔻"
        else: prefix = "⚖️"
        return f"{prefix} {COMPANY_NAMES.get(t, t)} ({t})"

    selected_ticker = st.selectbox("اختر السهم:", filtered_tickers, format_func=format_ticker, label_visibility="collapsed")

    # --- رسم الشارت ---
    tf_config = TIMEFRAMES[selected_timeframe]
    
    # 🌟 هنا التحديث الفوري: كل ما تغير الفريم، بيجيب الداتا من جديد ويظهر Spinner
    with st.spinner(f"جاري تحديث بيانات {selected_ticker} لفريم {selected_timeframe}..."):
        df = fetch_data(selected_ticker, tf_config["interval"], tf_config["period"])

    if not df.empty:
        current_price = df['Close'].iloc[-1].item()
        prev_close = df['Close'].iloc[-2].item()
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        color = "#00c853" if change >= 0 else "#ff3d00"
        sign = "+" if change >= 0 else ""

        st.markdown(f"""
        <div class="top-bar">
            <span class="ticker-name">{COMPANY_NAMES.get(selected_ticker, selected_ticker)} · {selected_ticker} · {selected_timeframe}</span>
            <span class="ohlc-data">C {current_price:.2f}</span>
            <span class="{'green-text' if change >= 0 else 'red-text'}" style="font-weight:bold;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</span>
        </div>
        """, unsafe_allow_html=True)

        df_plot = df.tail(100).copy()
        df_plot['SMA_20'] = df['Close'].rolling(window=20).mean().tail(100)
        df_plot['SMA_30'] = df['Close'].rolling(window=30).mean().tail(100)
        df_plot['SMA_50'] = df['Close'].rolling(window=50).mean().tail(100)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
        fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Price", increasing_line_color='#089981', decreasing_line_color='#f23645'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#ff9800', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_30'], mode='lines', name='SMA 30', line=dict(color='#2196f3', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#9c27b0', width=1.5)), row=1, col=1)
        
        colors = ['#089981' if close >= open else '#f23645' for open, close in zip(df_plot['Open'], df_plot['Close'])]
        fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], name="Volume", marker_color=colors), row=2, col=1)
        fig.update_layout(template="plotly_dark", paper_bgcolor='#131722', plot_bgcolor='#131722', height=400, autosize=True, margin=dict(l=5, r=5, t=5, b=5), showlegend=False, dragmode="pan", hovermode="x unified", uirevision='constant', xaxis=dict(showgrid=True, gridcolor='#2a2e39', fixedrange=False), yaxis=dict(showgrid=True, gridcolor='#2a2e39', side='right', fixedrange=False))
        fig.update_yaxes(showgrid=False, side='right', row=2, col=1, fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

with col_sidebar:
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
        <div style="text-align: center; font-weight: bold; font-size: 14px; color: {score_color}; margin-bottom: 5px;">{recommendation}</div>
        
        <div class="points-details">
            <b>تفصيل النقاط:</b><br>
            {breakdown}
        </div>
        
        <div style="border-top: 1px solid #2a2e39; margin: 8px 0;"></div>
        <p class="price-text" style="color: {color};">${current_price:.2f}</p>
        <p class="change-text" style="color: {color}; margin-top: 5px;">{sign}{change:.2f} ({sign}{change_pct:.2f}%)</p>
        
        <div style="background: {score_color}15; padding: 8px; border-radius: 5px; margin-top: 10px;">
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
                            <div style="border-top: 1px dashed #2a2e39; margin: 6px 0;"></div>
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
        <div class="side-card general-card" style="border-left-color: #ff9800;">
        <div class="card-title">📰 أخبار السهم</div>
        {news_html}
        </div>
        """, unsafe_allow_html=True)
