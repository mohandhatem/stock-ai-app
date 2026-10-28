import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
import datetime
import time
import pytz
import os

# ==========================================
# استيراد المكتبات الاختيارية (لجلب عقود الخيارات)
# ==========================================
try:
    from lumiwealth_tradier import Tradier
    TRADIER_AVAILABLE = True
except ImportError:
    TRADIER_AVAILABLE = False

try:
    from schwab import auth, client
    SCHWAB_AVAILABLE = True
except ImportError:
    SCHWAB_AVAILABLE = False

try:
    from polygon import RESTClient
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp { background-color: #000000; color: #ffffff; }
.block-container { padding-top: 0.5rem; padding-bottom: 2rem; max-width: 100%; }
div[data-baseweb="select"] input { pointer-events: none !important; user-select: none !important; caret-color: transparent !important; }
.top-bar { display: flex; align-items: center; justify-content: space-between; padding: 5px 10px; font-family: sans-serif; margin-bottom: 5px;}
.ticker-name { font-size: 22px; font-weight: bold; color: #fff; }
.side-card { background-color: #131722; border: 1px solid #2a2e39; border-radius: 8px; padding: 15px; margin-bottom: 15px;}
.live-card { border-left: 4px solid #00c853; }
.options-card { border-left: 4px solid #00bcd4; }
.general-card { border-left: 4px solid #ff9800; }
.card-title { color: #d1d4dc; font-size: 15px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #2a2e39; padding-bottom: 5px;}
.tv-price-box { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin-bottom: 15px; }
.tv-live-price { font-size: 38px; font-weight: bold; color: #fff; margin: 0; line-height: 1; letter-spacing: -0.5px;}
.tv-currency { font-size: 18px; color: #b2b5be; font-weight: normal;}
.tv-live-change { font-size: 18px; font-weight: 600; margin: 5px 0 15px 0; letter-spacing: 0.5px;}
.tv-pre-label { font-size: 13px; color: #ff9800; margin: 0; display: flex; align-items: center; gap: 5px; font-weight: bold;}
.tv-pre-price { font-size: 22px; font-weight: bold; color: #fff; margin: 2px 0 0 0; line-height: 1;}
.tv-pre-change { font-size: 14px; font-weight: 600; margin: 3px 0 0 0;}
.rec-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;}
.rec-label { color: #888; }
.news-item { font-size: 12px; margin-bottom: 8px; color: #d1d4dc; line-height: 1.4;}
.points-details { font-size: 11px; color: #9ca3af; text-align: right; margin-top: 5px; line-height: 1.6; border-top: 1px dashed #2a2e39; padding-top: 8px; }
.greeks-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; border-top: 1px dashed #2a2e39; padding-top: 15px;}
.greeks-item { display: flex; justify-content: space-between; font-size: 12px; background: #1e222d; padding: 6px 10px; border-radius: 4px;}
.greeks-label { color: #888; }
.greeks-value { color: #00bcd4; font-weight: bold; }
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { background-color: #131722; border-radius: 5px 5px 0 0; padding: 10px 20px; color: #d1d4dc;}
.stTabs [aria-selected="true"] { background-color: #1e222d; color: #00c853; border-bottom: 2px solid #00c853; }
[data-testid="stDataFrame"] { background-color: #131722; color: white; }
.stPlotlyChart { background-color: #000000; padding-bottom: 5px;}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, limit=None, key="live_refresh")

# ==========================================
# 2. إعدادات مفاتيح API (ضع مفاتيحك هنا إذا كانت لديك)
# ==========================================
TRADIER_TOKEN = os.environ.get("TRADIER_TOKEN", "")
TRADIER_ACCT = os.environ.get("TRADIER_ACCT", "")
SCHWAB_APP_KEY = os.environ.get("SCHWAB_APP_KEY", "")
SCHWAB_APP_SECRET = os.environ.get("SCHWAB_APP_SECRET", "")
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "")

def get_market_session():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(eastern)
    if now.weekday() >= 5: return "CLOSED"
    current_time = now.time()
    if datetime.time(9, 30) <= current_time < datetime.time(16, 0): return "REGULAR"
    elif datetime.time(4, 0) <= current_time < datetime.time(9, 30): return "PRE"
    elif datetime.time(16, 0) <= current_time < datetime.time(20, 0): return "POST"
    else: return "CLOSED"

# ==========================================
# 3. البيانات والقوائم
# ==========================================
US_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", "JPM", "V", "WMT", "DIS", "ORCL", "CRM", "ADBE", "AVGO", "QCOM", "BAC", "GS", "MA", "PYPL", "COST", "NKE", "SBUX", "MCD", "JNJ", "UNH", "PFE", "LLY", "XOM", "CVX", "BA", "PLTR", "IBM", "GE", "CAT", "MMM", "HON", "UPS", "FDX", "T", "VZ", "TMUS", "CMCSA", "CSCO", "TXN", "AMAT", "MU", "LRCX", "SBRC", "SHOP", "SQ", "ROKU", "ZM", "DOCU", "SNOW", "U", "RBLX", "COIN", "HOOD", "SOFI", "AI", "PATH", "NET", "DDOG", "CRWD", "OKTA", "PANW", "SMCI"]
INDICES = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT", "VIX (التقلب)": "^VIX", "TASI (تاسي)": "^TASI.SR"}
COMPANY_NAMES = {
    "^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones", "^RUT": "Russell 2000", "^VIX": "VIX", "^TASI.SR": "TASI (تاسي)",
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "TSLA": "Tesla", 
    "NVDA": "NVIDIA", "META": "Meta", "NFLX": "Netflix", "AMD": "AMD", "INTC": "Intel", "JPM": "JPMorgan", "V": "Visa", "WMT": "Walmart", "DIS": "Disney", "ORCL": "Oracle", "CRM": "Salesforce", "ADBE": "Adobe", "AVGO": "Broadcom", "QCOM": "Qualcomm", "BAC": "Bank of America", "GS": "Goldman Sachs", "MA": "Mastercard", "PYPL": "PayPal", "COST": "Costco", "NKE": "Nike", "SBUX": "Starbucks", "MCD": "McDonald's", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "PFE": "Pfizer", "LLY": "Eli Lilly", "XOM": "Exxon Mobil", "CVX": "Chevron", "BA": "Boeing", "PLTR": "Palantir", "IBM": "IBM", "GE": "General Electric", "CAT": "Caterpillar", "MMM": "3M", "HON": "Honeywell", "UPS": "UPS", "FDX": "FedEx", "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobile", "CMCSA": "Comcast", "CSCO": "Cisco", "TXN": "Texas Instruments", "AMAT": "Applied Materials", "MU": "Micron", "LRCX": "Lam Research", "SBRC": "Sound Equity", "SHOP": "Shopify", "SQ": "Block (Square)", "ROKU": "Roku", "ZM": "Zoom", "DOCU": "DocuSign", "SNOW": "Snowflake", "U": "Unity", "RBLX": "Roblox", "COIN": "Coinbase", "HOOD": "Robinhood", "SOFI": "SoFi", "AI": "C3.ai", "PATH": "UiPath", "NET": "Cloudflare", "DDOG": "Datadog", "CRWD": "CrowdStrike", "OKTA": "Okta", "PANW": "Palo Alto", "SMCI": "Super Micro Computer"
}
MARKETS = {"🇺🇸 أمريكي (US)": US_TICKERS, "📊 المؤشرات (Indices)": list(INDICES.keys())}
TIMEFRAMES = {"1m": {"interval": "1m", "period": "7d"}, "5m": {"interval": "5m", "period": "60d"}, "15m": {"interval": "15m", "period": "60d"}, "30m": {"interval": "30m", "period": "60d"}, "1h": {"interval": "60m", "period": "730d"}, "1d": {"interval": "1d", "period": "5y"}}

# ==========================================
# 4. دوال جلب البيانات الأساسية
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

@st.cache_data(ttl=5)
def get_live_quote(ticker):
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        live_price = fi.last_price
        prev_close = fi.previous_close
        if not live_price:
            df_reg = t.history(period="1d", interval="1m", prepost=False)
            if not df_reg.empty: live_price = df_reg['Close'].iloc[-1]
        if not prev_close:
            df_daily = t.history(period="5d", interval="1d")
            if len(df_daily) > 1: prev_close = df_daily['Close'].iloc[-2]
        if not live_price: return None
        if not prev_close: prev_close = live_price

        live_change = live_price - prev_close
        live_change_pct = (live_change / prev_close) * 100
        session = get_market_session()
        
        pre_price = None; pre_change = None; pre_change_pct = None
        if session in ["PRE", "CLOSED"]:
            info = t.info
            temp_pre = info.get('preMarketPrice')
            if not temp_pre:
                try:
                    df_m = t.history(period="1d", interval="1m", prepost=True)
                    if not df_m.empty:
                        df_m.index = df_m.index.tz_convert('America/New_York')
                        pre_df = df_m[df_m.index.time < datetime.time(9, 30)]
                        if not pre_df.empty: temp_pre = pre_df['Close'].iloc[-1]
                except: pass
            if temp_pre:
                pre_price = temp_pre
                pre_change = pre_price - prev_close
                pre_change_pct = (pre_change / prev_close) * 100

        return {"live_price": live_price, "live_change": live_change, "live_change_pct": live_change_pct, "pre_price": pre_price, "pre_change": pre_change, "pre_change_pct": pre_change_pct, "session": session}
    except: return None

@st.cache_data(ttl=300)
def fetch_news(ticker):
    try:
        news = yf.Ticker(ticker).news
        return [n['title'] for n in news[:3]] if news else []
    except: return []

# ==========================================
# 5. محرك التحليل الفني (المعادلة الذهبية)
# ==========================================
def calculate_technical_score(df, ticker, live_price):
    if df.empty or len(df) < 50 or not live_price: return 50, False, False, "بيانات غير كافية", 0, 0, 0, "لا توجد بيانات"
    close, high, low, volume = df['Close'], df['High'], df['Low'], df['Volume']
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else sma50
    is_uptrend = (live_price > sma50) and (sma50 > sma200)
    is_downtrend = (live_price < sma50) and (sma50 < sma200)
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_bullish = macd.iloc[-1] > signal.iloc[-1]
    
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low)).iloc[-1]
    stoch_d = (100 * ((close - lowest_low) / (highest_high - lowest_low))).rolling(window=3).mean().iloc[-1]
    stoch_bullish = stoch_k > stoch_d and stoch_k < 80
    williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low)).iloc[-1]
    
    avg_vol = volume.rolling(20).mean().iloc[-1]
    vol_spike = volume.iloc[-1] > (avg_vol * 1.5)
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    obv_uptrend = obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]
    
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    near_upper_bb = live_price >= bb_upper.iloc[-1]
    near_lower_bb = live_price <= bb_lower.iloc[-1]

    score = 50
    breakdown = []
    
    if is_uptrend: score += 15; breakdown.append("اتجاه صاعد قوي (Trend)")
    elif is_downtrend: score -= 15; breakdown.append("اتجاه هابط قوي (Trend)")
    else: breakdown.append("اتجاه عرضي (Trend)")

    if macd_bullish and 50 <= rsi < 70: score += 10; breakdown.append("زخم إيجابي (MACD+RSI)")
    elif not macd_bullish and rsi >= 70: score -= 5; breakdown.append("تشبع شرائي (RSI)")
    elif stoch_bullish: score += 5; breakdown.append("تقاطع ستوكاستيك إيجابي")
    if williams_r < -80: score += 5; breakdown.append("تشبع بيعي (Williams %R)")

    if vol_spike and obv_uptrend: score += 15; breakdown.append("تدفق سيولة وحجم قوي")
    elif not obv_uptrend: score -= 10; breakdown.append("ضعف في السيولة (OBV)")

    recent_high = high.tail(20).max()
    if live_price >= recent_high * 0.99: score += 10; breakdown.append("اختراق قمة سعرية")
    elif near_lower_bb: score += 5; breakdown.append("ارتداد من دعم بولينجر")

    score = max(10, min(95, score))
    
    if score >= 75:
        rec = "شراء قوي (STRONG BUY)"
        entry = live_price; t1 = live_price + (atr * 1.5); t2 = live_price + (atr * 3.0); stop = live_price - (atr * 1.5)
    elif score >= 60:
        rec = "شراء (BUY)"
        entry = live_price; t1 = live_price + (atr * 1.0); t2 = live_price + (atr * 2.0); stop = live_price - (atr * 1.2)
    elif score <= 25:
        rec = "بيع قوي (STRONG SELL)"
        entry = live_price; t1 = live_price - (atr * 1.5); t2 = live_price - (atr * 3.0); stop = live_price + (atr * 1.5)
    elif score <= 40:
        rec = "بيع (SELL)"
        entry = live_price; t1 = live_price - (atr * 1.0); t2 = live_price - (atr * 2.0); stop = live_price + (atr * 1.2)
    else:
        rec = "احتفاظ (HOLD)"
        entry = live_price; t1 = live_price; t2 = live_price; stop = live_price

    return score, is_uptrend, is_downtrend, rec, t1, t2, stop, "<br>".join(breakdown)

@st.cache_data(ttl=600)
def evaluate_tickers(tickers, interval, period):
    results = {}
    for t in tickers:
        try:
            df = fetch_data(t, interval, period)
            quote = get_live_quote(t)
            if len(df) < 50 or not quote: continue
            score, is_uptrend, is_downtrend, rec, _, _, _, _ = calculate_technical_score(df, t, quote['live_price'])
            results[t] = {'score': score, 'is_above_mas': is_uptrend, 'is_below_mas': is_downtrend, 'rec': rec}
            time.sleep(0.2) 
        except: pass
    return results

# ==========================================
# 6. دالة جلب عقود الخيارات (نظام التبديل التلقائي)
# ==========================================
@st.cache_data(ttl=300)
def get_option_chain_fallback(ticker):
    if not ticker.isalpha(): return None, "NOT_US_STOCK"

    # 1. yfinance
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        if expirations:
            chain = stock.option_chain(expirations[0])
            if not chain.calls.empty and not chain.puts.empty:
                return {"calls": chain.calls, "puts": chain.puts, "expiration": expirations[0]}, "yfinance"
    except: pass

    # 2. Tradier
    if TRADIER_AVAILABLE and TRADIER_TOKEN:
        try:
            tradier = Tradier(TRADIER_ACCT, TRADIER_TOKEN, is_paper=True)
            exps_resp = tradier.market.get_options_expirations(ticker)
            exps = exps_resp['expirations']['date']
            if exps:
                chain_data = tradier.market.get_chains(ticker, exps[0], greeks=True)
                calls = pd.DataFrame(chain_data['options']['option'])
                calls = calls[calls['option_type'] == 'call']
                puts = pd.DataFrame(chain_data['options']['option'])
                puts = puts[puts['option_type'] == 'put']
                if not calls.empty and not puts.empty:
                    return {"calls": calls, "puts": puts, "expiration": exps[0]}, "Tradier"
        except: pass

    # 3. Polygon
    if POLYGON_AVAILABLE and POLYGON_API_KEY:
        try:
            client_poly = RESTClient(POLYGON_API_KEY)
            contracts = []
            for c in client_poly.list_options_contracts(ticker, expired=False, limit=10):
                contracts.append(c)
            if contracts:
                calls = pd.DataFrame([c.__dict__ for c in contracts if c.contract_type == 'call'])
                puts = pd.DataFrame([c.__dict__ for c in contracts if c.contract_type == 'put'])
                if not calls.empty and not puts.empty:
                    return {"calls": calls, "puts": puts, "expiration": "N/A"}, "Polygon"
        except: pass

    return None, "NO_DATA"

@st.cache_data(ttl=300)
def get_options_recommendation(ticker, current_price, general_rec):
    if not ticker.isalpha(): return "NOT_US_STOCK"

    chain_data, source = get_option_chain_fallback(ticker)
    if chain_data is None: return "NO_DATA"

    calls = chain_data['calls']; puts = chain_data['puts']
    expiration = chain_data['expiration']

    try:
        if "شراء" in general_rec:
            chosen = calls.loc[abs(calls['strike'] - current_price).idxmin()]
            option_type = "Call (ATM)"
        elif "بيع" in general_rec:
            chosen = puts.loc[abs(puts['strike'] - current_price).idxmin()]
            option_type = "Put (ATM)"
        else:
            return "NO_OPTION_FOR_HOLD"
            
        last_price = chosen.get('lastPrice', chosen.get('last', 0))
        strike = chosen.get('strike', 0)
        if last_price == 0: return "NO_DATA"

        iv = chosen.get('impliedVolatility', chosen.get('implied_volatility', 0)) * 100
        delta = chosen.get('delta', 0); gamma = chosen.get('gamma', 0)
        theta = chosen.get('theta', 0); vega = chosen.get('vega', 0); rho = chosen.get('rho', 0)
        volume = chosen.get('volume', 0); oi = chosen.get('openInterest', chosen.get('open_interest', 0))

        intrinsic = 0
        if "Call" in option_type and current_price > strike: intrinsic = current_price - strike
        elif "Put" in option_type and current_price < strike: intrinsic = strike - current_price
        extrinsic = last_price - intrinsic if last_price > intrinsic else 0

        return {
            "type": option_type, "expiration": expiration, "strike": strike, "last_price": last_price,
            "session_target": last_price * 1.30, "expiry_target": last_price * 2.00, "stop_loss": last_price * 0.80,
            "iv": iv, "delta": delta, "gamma": gamma, "theta": theta, "vega": vega, "rho": rho,
            "volume": volume, "oi": oi, "intrinsic": intrinsic, "extrinsic": extrinsic,
            "source": source
        }
    except: return "NO_DATA"

# ==========================================
# 7. تحديث السعر كل ثانية (Fragment)
# ==========================================
@st.fragment(run_every="1s")
def render_price_box(ticker):
    quote = get_live_quote(ticker)
    if quote:
        live_price = quote.get('live_price')
        live_change = quote.get('live_change', 0)
        live_change_pct = quote.get('live_change_pct', 0)
        session = quote.get('session', 'CLOSED')
        
        main_color = "#00c853" if live_change >= 0 else "#ff3d00"
        main_sign = "+" if live_change >= 0 else ""

        pre_html = ""
        if quote.get('pre_price') and session != "REGULAR":
            pre_color = "#00c853" if quote.get('pre_change', 0) >= 0 else "#ff3d00"
            pre_sign = "+" if quote.get('pre_change', 0) >= 0 else ""
            pre_html = f"""
<p class="tv-pre-label">🌗 Pre-market</p>
<p class="tv-pre-price">{quote.get('pre_price'):.2f} <span class="tv-currency">USD</span></p>
<p class="tv-pre-change" style="color: {pre_color};">{pre_sign}{quote.get('pre_change', 0):.2f} ({pre_sign}{quote.get('pre_change_pct', 0):.2f}%)</p>
"""
        elif session == "REGULAR":
             pre_html = f"""<p class="tv-pre-label" style="color:#00c853;">🟢 السوق مفتوح (Regular Session)</p>"""

        st.markdown(f"""
<div class="tv-price-box">
<p class="tv-live-price">{live_price:.2f} <span class="tv-currency">USD</span></p>
<p class="tv-live-change" style="color: {main_color};">{main_sign}{live_change:.2f} ({main_sign}{live_change_pct:.2f}%)</p>
{pre_html}
</div>
""", unsafe_allow_html=True)

# ==========================================
# 8. واجهة المستخدم
# ==========================================
c1, c2, c3 = st.columns([1.5, 1.5, 1])
with c1: selected_market = st.selectbox("السوق", list(MARKETS.keys()), index=0, label_visibility="collapsed")
with c2: filter_mode = st.selectbox("الفلتر", ["الكل ⚖️", "إيجابي (فوق المتوسطات) 🚀", "سلبي (تحت المتوسطات) 🔻"], label_visibility="collapsed")
with c3: selected_timeframe = st.selectbox("الإطار", list(TIMEFRAMES.keys()), index=3, label_visibility="collapsed")

tf_config = TIMEFRAMES[selected_timeframe]

if selected_market == "📊 المؤشرات (Indices)":
    ticker_symbols = list(INDICES.values()); custom_ticker = st.text_input("أو اكتب رمز المؤشر يدوياً (مثال: ^GSPC):", "").strip().upper()
else:
    ticker_symbols = US_TICKERS; custom_ticker = st.text_input("أو اكتب رمز السهم يدوياً (مثال: AAPL, TSLA):", "").strip().upper()

with st.spinner(f"جاري تحليل البيانات بالمعادلة الذهبية..."):
    eval_data = evaluate_tickers(ticker_symbols, tf_config["interval"], tf_config["period"])

if filter_mode == "إيجابي (فوق المتوسطات) 🚀": filtered_tickers = [t for t in ticker_symbols if eval_data.get(t, {}).get('is_above_mas', False)]
elif filter_mode == "سلبي (تحت المتوسطات) 🔻": filtered_tickers = [t for t in ticker_symbols if eval_data.get(t, {}).get('is_below_mas', False)]
else: filtered_tickers = ticker_symbols

if not filtered_tickers:
    st.warning(f"لا توجد أسهم تتطابق مع الفلتر المختار ({filter_mode}). تم عرض كل الأسهم بدلاً من ذلك.")
    filtered_tickers = ticker_symbols

filtered_tickers = sorted(filtered_tickers, key=lambda x: eval_data.get(x, {}).get('score', 0), reverse=True)

def format_ticker(t):
    data = eval_data.get(t, {'is_above_mas': False, 'is_below_mas': False, 'score': 50})
    if data.get('is_above_mas'): prefix = "🚀"
    elif data.get('is_below_mas'): prefix = "🔻"
    else: prefix = "⚖️"
    display_name = COMPANY_NAMES.get(t, t) 
    return f"{prefix} {display_name} ({t}) - {data.get('score', 50)}%" if display_name != t else f"{prefix} {t} - {data.get('score', 50)}%"

selected_ticker = st.selectbox("اختر السهم:", filtered_tickers, format_func=format_ticker, label_visibility="collapsed")
if custom_ticker: selected_ticker = custom_ticker

if selected_ticker:
    df = fetch_data(selected_ticker, tf_config["interval"], tf_config["period"])
    quote = get_live_quote(selected_ticker)

    if not df.empty and quote:
        score, is_uptrend, is_downtrend, recommendation, t1, t2, stop, breakdown = calculate_technical_score(df, selected_ticker, quote['live_price'])
        score_color = "#00c853" if score >= 60 else ("#ff3d00" if score <= 40 else "#ff9800")

        tab1, tab2 = st.tabs(["📊 التحليل الفني والتوصيات", "⛓️ سلسلة الخيارات (Options Chain)"])

        with tab1:
            df_plot = df.tail(100).copy()
            df_plot['SMA_50'] = df['Close'].rolling(window=50).mean().tail(100)
            df_plot['SMA_200'] = df['Close'].rolling(window=200).mean().tail(100) if len(df) >= 200 else df_plot['SMA_50']

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
            fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Price", increasing_line_color='#00c853', decreasing_line_color='#ff3d00'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#ff9800', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['SMA_200'], mode='lines', name='SMA 200', line=dict(color='#2196f3', width=1.2)), row=1, col=1)
            colors = ['#00c853' if close >= open else '#ff3d00' for open, close in zip(df_plot['Open'], df_plot['Close'])]
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], name="Volume", marker_color=colors), row=2, col=1)
            fig.update_layout(template="plotly_dark", paper_bgcolor='#000000', plot_bgcolor='#000000', height=350, autosize=True, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, dragmode=False, hovermode="x unified", xaxis=dict(showgrid=True, gridcolor='#2a2e39', fixedrange=False), yaxis=dict(showgrid=True, gridcolor='#2a2e39', side='right', fixedrange=False))
            fig.update_yaxes(showgrid=False, side='right', row=2, col=1, fixedrange=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

            st.markdown(f"""
<div class="side-card live-card" style="border-left-color: {score_color};">
<div class="card-title">🧠 محرك التحليل (المعادلة الذهبية)</div>
<div style="background: {score_color}20; border: 1px solid {score_color}; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 15px;">
<div style="font-size: 24px; font-weight: bold; color: {score_color};">درجة الثقة: {score}%</div>
<div style="font-size: 16px; font-weight: bold; color: {score_color}; margin-top: 5px;">{recommendation}</div>
</div>
""", unsafe_allow_html=True)

            render_price_box(selected_ticker)

            st.markdown(f"""
<div class="points-details"><b>تفصيل النقاط:</b><br>{breakdown}</div>
<div style="border-top: 1px solid #2a2e39; margin: 10px 0;"></div>
<div style="background: {score_color}15; padding: 10px; border-radius: 5px; margin-top: 10px;">
<div class="rec-item"><span class="rec-label">الهدف الأول:</span> <span style="color:{score_color}; font-weight:bold;">${t1:.2f}</span></div>
<div class="rec-item"><span class="rec-label">الهدف الثاني:</span> <span style="color:{score_color}; font-weight:bold;">${t2:.2f}</span></div>
<div class="rec-item"><span class="rec-label">وقف الخسارة:</span> <span style="color:#ff3d00; font-weight:bold;">${stop:.2f}</span></div>
</div>
</div>
""", unsafe_allow_html=True)

            options_rec = get_options_recommendation(selected_ticker, quote['live_price'], recommendation)
            
            if options_rec == "NOT_US_STOCK":
                st.markdown('<div class="side-card options-card"><div class="card-title">📄 عقود الخيارات</div><div class="news-item">عقود الخيارات متاحة للأسهم الأمريكية فقط.</div></div>', unsafe_allow_html=True)
            elif options_rec == "NO_DATA":
                st.markdown('<div class="side-card options-card"><div class="card-title">📄 عقود الخيارات</div><div class="news-item">⚠️ جميع المصادر رفضت جلب البيانات. تأكد من مفاتيح API أو حاول لاحقاً.</div></div>', unsafe_allow_html=True)
            elif options_rec == "NO_OPTION_FOR_HOLD":
                st.markdown('<div class="side-card options-card"><div class="card-title">📄 عقود الخيارات</div><div class="news-item">التوصية الحالية "احتفاظ"، لا يفضل فتح عقود خيارات الآن.</div></div>', unsafe_allow_html=True)
            elif options_rec:
                st.markdown(f"""
<div class="side-card options-card">
<div class="card-title">📄 توصية عقود الخيارات (المصدر: {options_rec.get('source', 'N/A')})</div>
<div class="rec-item"><span class="rec-label">النوع:</span> <span style="color:#00bcd4; font-weight:bold;">{options_rec['type']}</span></div>
<div class="rec-item"><span class="rec-label">تاريخ الانتهاء:</span> <span>{options_rec['expiration']}</span></div>
<div class="rec-item"><span class="rec-label">Strike:</span> <span>${options_rec['strike']:.2f}</span></div>
<div class="rec-item"><span class="rec-label">سعر العقد:</span> <span style="color:#fff; font-weight:bold;">${options_rec['last_price']:.2f}</span></div>
<div style="border-top: 1px dashed #2a2e39; margin: 8px 0;"></div>
<div class="rec-item"><span class="rec-label">هدف الجلسة (+30%):</span> <span style="color:#00c853; font-weight:bold;">${options_rec['session_target']:.2f}</span></div>
<div class="rec-item"><span class="rec-label">هدف الانتهاء (+100%):</span> <span style="color:#00c853; font-weight:bold;">${options_rec['expiry_target']:.2f}</span></div>
<div class="rec-item"><span class="rec-label">وقف الخسارة (-20%):</span> <span style="color:#ff3d00; font-weight:bold;">${options_rec['stop_loss']:.2f}</span></div>

<div class="greeks-grid">
<div class="greeks-item"><span class="greeks-label">الحجم:</span> <span class="greeks-value">{options_rec['volume']}</span></div>
<div class="greeks-item"><span class="greeks-label">OI:</span> <span class="greeks-value">{options_rec['oi']}</span></div>
<div class="greeks-item"><span class="greeks-label">IV:</span> <span class="greeks-value">{options_rec['iv']:.2f}%</span></div>
<div class="greeks-item"><span class="greeks-label">Delta:</span> <span class="greeks-value">{options_rec['delta']:.3f}</span></div>
<div class="greeks-item"><span class="greeks-label">Gamma:</span> <span class="greeks-value">{options_rec['gamma']:.3f}</span></div>
<div class="greeks-item"><span class="greeks-label">Theta:</span> <span class="greeks-value">{options_rec['theta']:.3f}</span></div>
<div class="greeks-item"><span class="greeks-label">Vega:</span> <span class="greeks-value">{options_rec['vega']:.3f}</span></div>
<div class="greeks-item"><span class="greeks-label">Rho:</span> <span class="greeks-value">{options_rec['rho']:.3f}</span></div>
</div>
</div>
""", unsafe_allow_html=True)

            news = fetch_news(selected_ticker)
            news_html = "".join([f"<div class='news-item'>• {n}</div>" for n in news]) if news else "<div class='news-item'>لا توجد أخبار حديثة.</div>"
            st.markdown(f'<div class="side-card general-card"><div class="card-title">📰 أخبار السهم</div>{news_html}</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown(f"### ⛓️ سلسلة الخيارات لسهم **{COMPANY_NAMES.get(selected_ticker, selected_ticker)}**")
            chain_data, source = get_option_chain_fallback(selected_ticker)
            
            if chain_data is None:
                st.warning("لا توجد خيارات متاحة لهذا السهم حالياً (جميع المصادر فشلت).")
            else:
                calls = chain_data['calls']; puts = chain_data['puts']; expiration = chain_data['expiration']
                st.info(f"المصدر: {source} | تاريخ الانتهاء: {expiration}")
                
                live_price = quote['live_price']
                def format_option_df(df, is_call=True):
                    if df.empty: return df
                    if is_call: df['Moneyness'] = np.where(df['strike'] < live_price, 'ITM 🟢', 'OTM 🔴')
                    else: df['Moneyness'] = np.where(df['strike'] > live_price, 'ITM 🟢', 'OTM 🔴')
                    
                    cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'Moneyness']
                    for greek in ['delta', 'gamma', 'theta', 'vega']:
                        if greek in df.columns: cols.append(greek)
                    
                    res = df[[c for c in cols if c in df.columns]].copy()
                    if 'impliedVolatility' in res.columns:
                        res['impliedVolatility'] = (res['impliedVolatility'] * 100).round(2).astype(str) + '%'
                    res = res.sort_values(by='strike')
                    
                    res.rename(columns={
                        'strike': 'Strike', 'lastPrice': 'Last Price', 'bid': 'Bid', 'ask': 'Ask',
                        'volume': 'Volume', 'openInterest': 'Open Int.', 'impliedVolatility': 'IV',
                        'Moneyness': 'Type', 'delta': 'Delta', 'gamma': 'Gamma', 'theta': 'Theta', 'vega': 'Vega'
                    }, inplace=True)
                    return res
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🟢 عقود الشراء (Calls)")
                    st.dataframe(format_option_df(calls, is_call=True), use_container_width=True, hide_index=True)
                with col2:
                    st.markdown("#### 🔴 عقود البيع (Puts)")
                    st.dataframe(format_option_df(puts, is_call=False), use_container_width=True, hide_index=True)
