"""
NOP Calculator — v3.1
Real-time Net Open Position monitoring for dealing desks.
Tracks metals (Gold, Silver) and indices (DJ30, NAS100, S&P500) + custom symbols.

Deploy: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NOP Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [data-testid="stApp"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0a0e17 !important;
}

/* ── Header ─────────────────────────────────── */
.dash-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6);
}
.dash-header h1 {
    font-size: 28px; font-weight: 700; color: #f8fafc;
    margin: 0 0 4px 0; letter-spacing: -0.5px;
}
.dash-header p {
    font-size: 13px; color: #94a3b8; margin: 0;
    letter-spacing: 0.5px; text-transform: uppercase;
}

/* ── Summary cards ───────────────────────────── */
.summary-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 8px;
}
.summary-card .label {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.2px; color: #64748b; margin-bottom: 8px;
}
.summary-card .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px; font-weight: 600; line-height: 1.1;
}
.summary-card .sub { font-size: 12px; color: #94a3b8; margin-top: 5px; }
.c-blue   .value { color: #3b82f6; }
.c-green  .value { color: #10b981; }
.c-amber  .value { color: #f59e0b; }
.c-red    .value { color: #ef4444; }
.c-purple .value { color: #8b5cf6; }
.c-cyan   .value { color: #06b6d4; }

/* ── Instrument cards ────────────────────────── */
.inst-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 8px;
}
.inst-card .sym {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700; font-size: 15px; color: #f1f5f9;
}
.dir-long  { color: #10b981; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.dir-short { color: #ef4444; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.dir-flat  { color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.lots-val  { font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 700; margin: 6px 0; }
.expo-row  { font-size: 12px; color: #94a3b8; margin: 2px 0; }
.bar-bg    { background: #1e293b; border-radius: 6px; height: 8px; margin-top: 12px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 6px; }
.bar-lbl   { font-size: 11px; color: #64748b; margin-top: 5px; display: flex; justify-content: space-between; }
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
}
.b-safe    { background: rgba(16,185,129,.15); color: #10b981; }
.b-warn    { background: rgba(245,158,11,.15);  color: #f59e0b; }
.b-breach  { background: rgba(239,68,68,.15);   color: #ef4444; }

/* ── Custom symbol pill ──────────────────────── */
.custom-tag {
    display: inline-block;
    background: rgba(139,92,246,.15);
    color: #a78bfa;
    font-size: 10px; font-weight: 600;
    padding: 2px 8px; border-radius: 10px;
    letter-spacing: 0.5px; text-transform: uppercase;
    margin-left: 6px;
}

/* ── Section header ──────────────────────────── */
.sec-hdr {
    font-size: 17px; font-weight: 700; color: #f1f5f9;
    margin: 28px 0 14px 0; padding-bottom: 10px;
    border-bottom: 1px solid #1e293b;
}

/* ── Formula box ─────────────────────────────── */
.formula-box {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid #2d2b55;
    border-radius: 12px;
    padding: 18px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; line-height: 2; color: #c4b5fd;
}
.formula-box span { color: #06b6d4; }

/* ── Risk HTML table ─────────────────────────── */
.risk-table {
    width: 100%; border-collapse: collapse;
    font-size: 13px; color: #f1f5f9;
    font-family: 'DM Sans', sans-serif;
}
.risk-table th {
    background: #1e293b; color: #94a3b8;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.8px;
    padding: 10px 12px; text-align: left; border: none;
}
.risk-table td {
    padding: 9px 12px; border-bottom: 1px solid #1e293b;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
}
.risk-table tr:hover td { background: #1a2235; }
.row-breach td { background: rgba(239,68,68,.08); color: #fca5a5; }
.row-warn   td { background: rgba(245,158,11,.06); color: #fcd34d; }
.td-green { color: #10b981; font-weight: 600; }
.td-red   { color: #ef4444; font-weight: 600; }

/* ── Sidebar ─────────────────────────────────── */
section[data-testid="stSidebar"] { background: #0f1629 !important; }
a.anchor-link { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
INSTRUMENTS = {
    "XAUUSD": {"name": "Gold",   "contract_size": 100,   "yahoo": "GC=F",  "default_price": 4500.00, "category": "Metals"},
    "XAGUSD": {"name": "Silver", "contract_size": 5000,  "yahoo": "SI=F",  "default_price": 68.00,   "category": "Metals"},
    "US30":   {"name": "DJ30",   "contract_size": 1,     "yahoo": "^DJI",  "default_price": 45577.00,"category": "Indices"},
    "US100":  {"name": "NAS100", "contract_size": 1,     "yahoo": "^NDX",  "default_price": 21648.00,"category": "Indices"},
    "US500":  {"name": "S&P500", "contract_size": 1,     "yahoo": "^GSPC", "default_price": 6506.00, "category": "Indices"},
}

NOP_OPTIONS = {"10M": 10_000_000, "50M": 50_000_000, "100M": 100_000_000, "200M": 200_000_000, "Custom": 0}
CATEGORIES  = ["Metals", "Indices", "Forex", "Crypto", "Energy", "Other"]

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def _default_row(symbol="XAUUSD", nop_preset="100M", nop_custom=100_000_000):
    cfg = INSTRUMENTS.get(symbol, {})
    return {
        "symbol":            symbol,
        "nop_preset":        nop_preset,
        "nop_custom":        nop_custom,
        "open_lots":         0.0,
        "price_override":    0.0,
        "contract_size":     cfg.get("contract_size", 1),   # editable
        # Custom symbol fields
        "custom_name":       "",
        "custom_ticker":     "",
        "custom_category":   "Metals",
    }

if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}
if "fetch_ts" not in st.session_state:
    st.session_state.fetch_ts = None
if "rows" not in st.session_state:
    st.session_state.rows = [
        _default_row("XAUUSD", "100M", 100_000_000),
        _default_row("XAGUSD", "10M",  10_000_000),
        _default_row("US30",   "100M", 100_000_000),
        _default_row("US100",  "100M", 100_000_000),
        _default_row("US500",  "100M", 100_000_000),
    ]
if "manual_rows" not in st.session_state:
    st.session_state.manual_rows = [
        {"name": "XAUUSD", "nop_m": 100.0, "open_lots": 0.0, "contract_size": 100, "price": 4500.0},
        {"name": "XAGUSD", "nop_m": 10.0,  "open_lots": 0.0, "contract_size": 5000, "price": 68.0},
        {"name": "US30",   "nop_m": 100.0, "open_lots": 0.0, "contract_size": 1,    "price": 45577.0},
        {"name": "US100",  "nop_m": 100.0, "open_lots": 0.0, "contract_size": 1,    "price": 21648.0},
        {"name": "US500",  "nop_m": 100.0, "open_lots": 0.0, "contract_size": 1,    "price": 6506.0},
    ]

# ══════════════════════════════════════════════════════════════════════════════
# PRICE FETCHER
# ══════════════════════════════════════════════════════════════════════════════
def fetch_prices(extra_tickers=None):
    """Fetch live prices via yfinance. extra_tickers = {local_sym: yahoo_ticker}"""
    fetched = {}
    try:
        import yfinance as yf
        ticker_map = {v["yahoo"]: k for k, v in INSTRUMENTS.items()}
        if extra_tickers:
            ticker_map.update({v: k for k, v in extra_tickers.items() if v})

        for yahoo_sym, local_sym in ticker_map.items():
            try:
                hist = yf.Ticker(yahoo_sym).history(period="5d")
                if not hist.empty:
                    close = hist["Close"].dropna().iloc[-1]
                    if close > 0:
                        fetched[local_sym] = round(float(close), 2)
            except Exception:
                pass
    except ImportError:
        pass
    return fetched


def get_price(symbol, custom_label=""):
    if symbol in st.session_state.live_prices:
        return st.session_state.live_prices[symbol]
    if symbol == "Custom":
        if custom_label and custom_label in st.session_state.live_prices:
            return st.session_state.live_prices[custom_label]
        return 0.0
    return INSTRUMENTS[symbol]["default_price"]


# ══════════════════════════════════════════════════════════════════════════════
# CALCULATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def compute_row(symbol, open_lots, nop_limit_usd, price_override=0.0,
                contract_size=None, custom_name="", custom_category="Metals", custom_ticker=""):
    """Compute all risk metrics. contract_size overrides instrument default when provided."""
    if symbol == "Custom":
        name     = custom_name or "Custom"
        category = custom_category
        default_cs = 1
        price = price_override if price_override > 0 else get_price(symbol, custom_name or custom_ticker)
    else:
        cfg      = INSTRUMENTS[symbol]
        name     = cfg["name"]
        category = cfg["category"]
        default_cs = cfg["contract_size"]
        price = price_override if price_override > 0 else get_price(symbol)

    cs = contract_size if (contract_size is not None and contract_size > 0) else default_cs
    notional   = price * cs
    nop_max    = (nop_limit_usd / notional) if notional else 0
    exposure   = abs(open_lots) * notional
    remaining  = nop_max - abs(open_lots)
    pnl_per_1  = abs(open_lots) * cs
    utilization = (exposure / nop_limit_usd * 100) if nop_limit_usd > 0 else 0
    margin_100 = notional / 100 if notional else 0
    direction  = "NET LONG" if open_lots > 0 else ("NET SHORT" if open_lots < 0 else "FLAT")
    return {
        "Symbol": symbol if symbol != "Custom" else (custom_name or "Custom"),
        "Name": name, "Category": category,
        "Contract Size": cs, "Price": price, "Open Lots": open_lots,
        "Direction": direction, "Notional/Lot": notional,
        "NOP Limit (USD)": nop_limit_usd, "NOP Max Lots": round(nop_max, 2),
        "Current Exposure": exposure, "Remaining Lots": round(remaining, 2),
        "PnL per $1": pnl_per_1, "Utilization %": round(utilization, 2),
        "Margin/Lot @100x": margin_100,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MANUAL CALCULATION ENGINE  (no yfinance, all inputs provided by user)
# ══════════════════════════════════════════════════════════════════════════════
def compute_manual(name, open_lots, nop_m, contract_size, price):
    """Pure offline calculation — all values supplied by the user."""
    nop_usd    = nop_m * 1_000_000
    notional   = price * contract_size
    nop_max    = (nop_usd / notional) if notional else 0
    exposure   = abs(open_lots) * notional
    remaining  = nop_max - abs(open_lots)
    pnl_per_1  = abs(open_lots) * contract_size
    utilization = (exposure / nop_usd * 100) if nop_usd > 0 else 0
    margin_100 = notional / 100 if notional else 0
    direction  = "NET LONG" if open_lots > 0 else ("NET SHORT" if open_lots < 0 else "FLAT")
    return {
        "Symbol":          name or "—",
        "Name":            name or "—",
        "Contract Size":   contract_size,
        "Price":           price,
        "Open Lots":       open_lots,
        "Direction":       direction,
        "Notional/Lot":    notional,
        "NOP Limit (USD)": nop_usd,
        "NOP Max Lots":    round(nop_max, 2),
        "Current Exposure": exposure,
        "Remaining Lots":  round(remaining, 2),
        "PnL per $1":      pnl_per_1,
        "Utilization %":   round(utilization, 2),
        "Margin/Lot @100x": margin_100,
        "Category":        "Manual",
    }


# ══════════════════════════════════════════════════════════════════════════════
# HTML TABLE RENDERERS
# ══════════════════════════════════════════════════════════════════════════════
def render_risk_table(results):
    cols = ["Symbol", "Direction", "Price", "Contract Size", "Open Lots",
            "Notional/Lot", "NOP Limit (USD)", "NOP Max Lots",
            "Current Exposure", "Remaining Lots", "PnL per $1", "Utilization %"]
    html = '<div style="overflow-x:auto;"><table class="risk-table"><thead><tr>'
    for c in cols:
        html += f'<th>{c}</th>'
    html += '</tr></thead><tbody>'
    for r in results:
        rem  = r["Remaining Lots"]
        util = r["Utilization %"]
        row_cls = "row-breach" if rem < 0 else ("row-warn" if util > 70 else "")
        html += f'<tr class="{row_cls}">'
        for c in cols:
            v = r[c]
            if c == "Direction":
                dcls = "td-green" if "LONG" in v else ("td-red" if "SHORT" in v else "")
                cell = f'<span class="{dcls}">{v}</span>'
            elif c == "Price":
                cell = f"${v:,.2f}"
            elif c in ("Notional/Lot", "NOP Limit (USD)", "Current Exposure", "PnL per $1"):
                cell = f"${v:,.0f}"
            elif c == "Open Lots":
                color = "#10b981" if v > 0 else ("#ef4444" if v < 0 else "#64748b")
                cell = f'<span style="color:{color}">{v:,.2f}</span>'
            elif c == "Remaining Lots":
                color = "#ef4444" if v < 0 else "#10b981"
                cell = f'<span style="color:{color};font-weight:600">{v:,.2f}</span>'
            elif c == "NOP Max Lots":
                cell = f"{v:,.2f}"
            elif c == "Utilization %":
                color = "#ef4444" if v > 80 else ("#f59e0b" if v > 50 else "#10b981")
                cell = f'<span style="color:{color}">{v:.1f}%</span>'
            elif c == "Contract Size":
                cell = f"{int(v):,}"
            else:
                cell = str(v)
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    return html


def render_scenario_table(scenario_rows):
    html = '<div style="overflow-x:auto;"><table class="risk-table"><thead><tr>'
    for c in ["Symbol", "Name", "Net Lots", "Contract Size", "Price Move", "PnL Impact ($)"]:
        html += f'<th>{c}</th>'
    html += '</tr></thead><tbody>'
    for r in scenario_rows:
        pnl   = r["PnL Impact ($)"]
        color = "#10b981" if pnl > 0 else ("#ef4444" if pnl < 0 else "#94a3b8")
        html += f'''<tr>
            <td>{r["Symbol"]}</td><td>{r["Name"]}</td>
            <td>{r["Net Lots"]:,.2f}</td><td>{r["Contract Size"]:,}</td>
            <td>${r["Price Move"]:,.2f}</td>
            <td><span style="color:{color};font-weight:600">${pnl:,.0f}</span></td>
        </tr>'''
    html += '</tbody></table></div>'
    return html


# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO SUMMARY CARDS
# ══════════════════════════════════════════════════════════════════════════════
def render_summary(results):
    df = pd.DataFrame(results)
    total_exposure = df["Current Exposure"].sum()
    total_lots     = df["Open Lots"].sum()
    total_pnl1     = df["PnL per $1"].sum()
    avg_util       = df["Utilization %"].mean()
    breach_count   = int((df["Remaining Lots"] < 0).sum())
    active_count   = int((df["Open Lots"].abs() > 0).sum())

    cards = [
        ("TOTAL EXPOSURE",     f"${total_exposure:,.0f}",        f"{total_exposure/1e6:.1f}M USD",    "c-blue"),
        ("NET OPEN LOTS",      f"{total_lots:,.2f}",             "Across all instruments",            "c-cyan"),
        ("PnL PER $1 MOVE",    f"${total_pnl1:,.0f}",           "Portfolio sensitivity",             "c-purple"),
        ("AVG UTILIZATION",    f"{avg_util:.1f}%",               "Of NOP limits",                     "c-amber" if avg_util > 40 else "c-green"),
        ("RISK BREACHES",      str(breach_count),                "Remaining < 0",                     "c-red" if breach_count > 0 else "c-green"),
        ("ACTIVE INSTRUMENTS", f"{active_count}/{len(results)}", "With open positions",               "c-cyan"),
    ]
    cols = st.columns(6)
    for col, (label, value, sub, cls) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="summary-card {cls}">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# INSTRUMENT BREAKDOWN CARDS
# ══════════════════════════════════════════════════════════════════════════════
def render_instrument_cards(results):
    card_cols = st.columns(min(len(results), 5))
    for idx, r in enumerate(results):
        with card_cols[idx % len(card_cols)]:
            direction = r["Direction"]
            dir_cls   = "dir-long" if "LONG" in direction else ("dir-short" if "SHORT" in direction else "dir-flat")
            lots_color = "#10b981" if r["Open Lots"] > 0 else ("#ef4444" if r["Open Lots"] < 0 else "#64748b")
            util       = r["Utilization %"]
            bar_color  = "#ef4444" if util > 80 else ("#f59e0b" if util > 50 else "#10b981")
            bar_width  = min(util, 100)
            status_cls = "b-breach" if r["Remaining Lots"] < 0 else ("b-warn" if util > 70 else "b-safe")
            status_txt = "BREACH" if r["Remaining Lots"] < 0 else ("WARNING" if util > 70 else "SAFE")
            rem_color  = "#ef4444" if r["Remaining Lots"] < 0 else "#10b981"
            st.markdown(f"""
            <div class="inst-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="sym">{r['Symbol']}</span>
                    <span class="badge {status_cls}">{status_txt}</span>
                </div>
                <div class="{dir_cls}" style="margin-top:5px;">{direction}</div>
                <div class="lots-val" style="color:{lots_color};">{r['Open Lots']:,.2f}
                    <span style="font-size:13px;color:#64748b;"> lots</span>
                </div>
                <div class="expo-row">Exposure: ${r['Current Exposure']:,.0f}</div>
                <div class="expo-row">Notional/Lot: ${r['Notional/Lot']:,.0f}</div>
                <div class="expo-row">PnL per $1: ${r['PnL per $1']:,.0f}</div>
                <div class="bar-bg"><div class="bar-fill" style="width:{bar_width}%;background:{bar_color};"></div></div>
                <div class="bar-lbl">
                    <span>Util: {util:.1f}%</span>
                    <span>Max: {r['NOP Max Lots']:,.1f} lots</span>
                </div>
                <div class="expo-row" style="margin-top:5px;">
                    Remaining: <b style="color:{rem_color}">{r['Remaining Lots']:,.2f}</b> lots
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
    <h1>📊 NOP Calculator</h1>
    <p>Net Open Position &nbsp;·&nbsp; Notional Exposure &nbsp;·&nbsp; Capacity Monitor &nbsp;·&nbsp; Dealing Desk RMS</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    if st.button("🔄 Fetch Live Prices", use_container_width=True, type="primary"):
        with st.spinner("Connecting to markets…"):
            # Collect custom tickers from Tab 1 rows only
            extra = {}
            for r in st.session_state.rows:
                if r["symbol"] == "Custom" and r.get("custom_ticker"):
                    label = r.get("custom_name") or r["custom_ticker"]
                    extra[label] = r["custom_ticker"]
            prices = fetch_prices(extra_tickers=extra if extra else None)
            if prices:
                st.session_state.live_prices.update(prices)
                st.session_state.fetch_ts = datetime.now().strftime("%H:%M:%S")
                st.success(f"Fetched {len(prices)} prices")
            else:
                st.warning("API unavailable — using defaults / manual")

    if st.session_state.fetch_ts:
        st.caption(f"Last fetch: {st.session_state.fetch_ts}")

    st.markdown("---")
    st.markdown("### 💹 Current Prices")
    for sym, cfg in INSTRUMENTS.items():
        p = get_price(sym)
        st.markdown(f"**{sym}** ({cfg['name']}): `${p:,.2f}`")

    st.markdown("---")
    st.markdown("### 📐 Formulas")
    st.markdown("""
    <div class="formula-box">
    <span>Notional/Lot</span> = Price × Contract Size<br>
    <span>NOP Max Lots</span> = NOP Limit / Notional<br>
    <span>Exposure</span> = |Open Lots| × Notional<br>
    <span>Remaining</span> = Max Lots − |Open Lots|<br>
    <span>PnL per $1</span> = |Open Lots| × Contract Size<br>
    <span>Utilization</span> = Exposure / NOP Limit × 100
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Default Contract Sizes")
    for sym, cfg in INSTRUMENTS.items():
        unit = "oz" if cfg["category"] == "Metals" else "unit"
        st.markdown(f"`{sym}` → **{cfg['contract_size']:,}** {unit}")

    st.markdown("---")
    st.caption("NOP Calculator v3.1 · Streamlit Cloud Ready")


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["📊 NOP Calculator", "✏️ Manual Entry"])


# ─────────────────────────────────────────────────────────────────────────────
# SHARED: row input renderer (used in both tabs)
# ─────────────────────────────────────────────────────────────────────────────
def render_row_inputs(i, row, key_prefix="t1"):
    """Renders input widgets for one position row. Returns updated row dict + computed result."""
    symbol_options = list(INSTRUMENTS.keys()) + ["✏️ Custom"]
    nop_labels     = list(NOP_OPTIONS.keys())

    # Map stored "Custom" → display "✏️ Custom"
    stored_sym = row.get("symbol", "XAUUSD")
    display_sym = "✏️ Custom" if stored_sym == "Custom" else stored_sym

    c1, c2, c3, c4, c5 = st.columns([1.3, 1.3, 1.2, 1.1, 1.1])

    with c1:
        sym_sel = st.selectbox("Symbol", symbol_options,
            index=symbol_options.index(display_sym) if display_sym in symbol_options else 0,
            key=f"{key_prefix}_sym_{i}")
        is_custom = (sym_sel == "✏️ Custom")
        sym = "Custom" if is_custom else sym_sel
        row["symbol"] = sym

    with c2:
        nop_choice = st.selectbox("NOP Limit", nop_labels,
            index=nop_labels.index(row.get("nop_preset", "100M")),
            key=f"{key_prefix}_nop_{i}")
        row["nop_preset"] = nop_choice
        if nop_choice == "Custom":
            nop_usd = st.number_input("Custom NOP (USD)",
                value=int(row.get("nop_custom", 100_000_000)),
                min_value=0, step=1_000_000, key=f"{key_prefix}_nopc_{i}")
        else:
            nop_usd = NOP_OPTIONS[nop_choice]
        row["nop_custom"] = nop_usd

    with c3:
        lots = st.number_input("Open Lots (net)", value=float(row.get("open_lots", 0.0)),
            step=0.01, format="%.2f", key=f"{key_prefix}_lots_{i}",
            help="+ve = Long, −ve = Short")
        row["open_lots"] = lots

    with c4:
        # Default contract size: from instrument or stored override
        if is_custom:
            default_cs = int(row.get("contract_size", 1)) or 1
        else:
            default_cs = int(row.get("contract_size", INSTRUMENTS[sym]["contract_size"]))
        cs_val = st.number_input("Contract Size", value=default_cs,
            min_value=1, step=1, key=f"{key_prefix}_cs_{i}",
            help="Editable — adjusts notional & all formulas")
        row["contract_size"] = cs_val

    with c5:
        p_over = st.number_input("Price Override", value=float(row.get("price_override", 0.0)),
            min_value=0.0, step=0.01, format="%.2f", key=f"{key_prefix}_po_{i}",
            help="0 = use live/default price")
        row["price_override"] = p_over

    # ── Custom symbol extra fields ──
    if is_custom:
        cx1, cx2, cx3 = st.columns([1.5, 1.5, 1])
        with cx1:
            cname = st.text_input("Symbol / Name", value=row.get("custom_name", ""),
                placeholder="e.g. EURUSD, BTCUSD", key=f"{key_prefix}_cname_{i}")
            row["custom_name"] = cname
        with cx2:
            cticker = st.text_input("Yahoo Finance Ticker", value=row.get("custom_ticker", ""),
                placeholder="e.g. EURUSD=X, BTC-USD", key=f"{key_prefix}_cticker_{i}",
                help="Used for Fetch Live Prices")
            row["custom_ticker"] = cticker
        with cx3:
            ccat = st.selectbox("Category", CATEGORIES,
                index=CATEGORIES.index(row.get("custom_category", "Metals")),
                key=f"{key_prefix}_ccat_{i}")
            row["custom_category"] = ccat

    result = compute_row(
        sym, lots, nop_usd, p_over,
        contract_size=cs_val,
        custom_name=row.get("custom_name", ""),
        custom_category=row.get("custom_category", "Metals"),
        custom_ticker=row.get("custom_ticker", ""),
    )
    return row, result


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — NOP CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-hdr">📝 Position & Limit Inputs</div>', unsafe_allow_html=True)
    st.caption("Select a symbol (or ✏️ Custom to add your own), set NOP limit, enter lots. Contract Size is fully editable — all formulas update automatically.")

    col_add, col_rem, _ = st.columns([1, 1, 4])
    with col_add:
        if st.button("➕ Add Row", use_container_width=True, key="t1_add"):
            st.session_state.rows.append(_default_row())
            st.rerun()
    with col_rem:
        if len(st.session_state.rows) > 1:
            if st.button("➖ Remove Last", use_container_width=True, key="t1_rem"):
                st.session_state.rows.pop()
                st.rerun()

    results = []
    for i, row in enumerate(st.session_state.rows):
        with st.container():
            updated_row, result = render_row_inputs(i, row, key_prefix="t1")
            st.session_state.rows[i] = updated_row
            results.append(result)
        if i < len(st.session_state.rows) - 1:
            st.markdown("<hr style='border:none;border-top:1px solid #1e293b;margin:6px 0;'>",
                        unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">📊 Portfolio Summary</div>', unsafe_allow_html=True)
    df = render_summary(results)

    st.markdown('<div class="sec-hdr">🔍 Instrument Breakdown</div>', unsafe_allow_html=True)
    render_instrument_cards(results)

    st.markdown('<div class="sec-hdr">📋 Full Risk Calculation Table</div>', unsafe_allow_html=True)
    st.markdown(render_risk_table(results), unsafe_allow_html=True)

    # ── Scenario Analysis ──
    st.markdown('<div class="sec-hdr">⚡ PnL Scenario Analysis</div>', unsafe_allow_html=True)
    st.caption("Estimated PnL if the market moves by the amounts below.")
    sc1, sc2, sc3 = st.columns(3)
    with sc1: move_gold   = st.number_input("Gold move ($)",    value=10.0,  step=1.0,  key="mv_g")
    with sc2: move_silver = st.number_input("Silver move ($)",  value=1.0,   step=0.10, key="mv_s")
    with sc3: move_index  = st.number_input("Index move (pts)", value=100.0, step=10.0, key="mv_i")

    scenario_rows = []
    for r in results:
        sym_key = r["Symbol"]
        mv = move_gold if sym_key == "XAUUSD" else (move_silver if sym_key == "XAGUSD" else move_index)
        pnl = r["Open Lots"] * r["Contract Size"] * mv
        scenario_rows.append({"Symbol": sym_key, "Name": r["Name"],
            "Net Lots": r["Open Lots"], "Contract Size": r["Contract Size"],
            "Price Move": mv, "PnL Impact ($)": pnl})

    st.markdown(render_scenario_table(scenario_rows), unsafe_allow_html=True)
    total_pnl_sc = sum(r["PnL Impact ($)"] for r in scenario_rows)
    pnl_color = "#10b981" if total_pnl_sc >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="summary-card" style="max-width:340px;margin-top:14px;">
        <div class="label">TOTAL PORTFOLIO PnL IMPACT</div>
        <div class="value" style="color:{pnl_color};font-size:30px;">${total_pnl_sc:,.0f}</div>
    </div>""", unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<div class="sec-hdr">📥 Export</div>', unsafe_allow_html=True)
    export_df = df[[
        "Symbol", "Name", "Contract Size", "Price", "Open Lots", "Direction",
        "NOP Limit (USD)", "Notional/Lot", "NOP Max Lots", "Current Exposure",
        "Remaining Lots", "PnL per $1", "Utilization %", "Margin/Lot @100x",
    ]].copy()
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, sheet_name="NOP Risk Report", index=False)
            pd.DataFrame(scenario_rows).to_excel(writer, sheet_name="Scenario Analysis", index=False)
        buffer.seek(0)
        ex1, ex2, _ = st.columns([1, 1, 3])
        with ex1:
            st.download_button("📥 Download Excel", data=buffer,
                file_name=f"NOP_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with ex2:
            st.download_button("📄 Download CSV", data=export_df.to_csv(index=False),
                file_name=f"NOP_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv", use_container_width=True)
    except Exception:
        st.download_button("📄 Download CSV", data=export_df.to_csv(index=False),
            file_name=f"NOP_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — MANUAL ENTRY  (fully offline, no yfinance)
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-hdr">✏️ Manual Position Entry</div>', unsafe_allow_html=True)
    st.caption("Type everything directly — symbol name, NOP in millions, lots, contract size, price. No internet required. Calculations update instantly.")

    ma1, ma2, _ = st.columns([1, 1, 4])
    with ma1:
        if st.button("➕ Add Row", use_container_width=True, key="m_add"):
            st.session_state.manual_rows.append(
                {"name": "", "nop_m": 100.0, "open_lots": 0.0, "contract_size": 1, "price": 0.0}
            )
            st.rerun()
    with ma2:
        if len(st.session_state.manual_rows) > 1:
            if st.button("➖ Remove Last", use_container_width=True, key="m_rem"):
                st.session_state.manual_rows.pop()
                st.rerun()

    manual_results = []

    for i, mrow in enumerate(st.session_state.manual_rows):
        with st.container():
            m1, m2, m3, m4, m5 = st.columns([1.2, 1.1, 1.2, 1.2, 1.2])

            with m1:
                mname = st.text_input("Symbol / Name", value=mrow.get("name", ""),
                    placeholder="e.g. XAUUSD", key=f"mname_{i}")
                st.session_state.manual_rows[i]["name"] = mname

            with m2:
                mnop_m = st.number_input("NOP Limit (M)", value=float(mrow.get("nop_m", 100.0)),
                    min_value=0.0, step=1.0, format="%.1f", key=f"mnop_{i}",
                    help="In millions — e.g. 100 = $100,000,000")
                st.session_state.manual_rows[i]["nop_m"] = mnop_m

            with m3:
                mlots = st.number_input("Open Lots", value=float(mrow.get("open_lots", 0.0)),
                    step=0.01, format="%.2f", key=f"mlots_{i}",
                    help="+ve = Long, −ve = Short")
                st.session_state.manual_rows[i]["open_lots"] = mlots

            with m4:
                mcs = st.number_input("Contract Size", value=int(mrow.get("contract_size", 1)),
                    min_value=1, step=1, key=f"mcs_{i}",
                    help="oz for metals, 1 for indices")
                st.session_state.manual_rows[i]["contract_size"] = mcs

            with m5:
                mprice = st.number_input("Price", value=float(mrow.get("price", 0.0)),
                    min_value=0.0, step=0.01, format="%.2f", key=f"mprice_{i}")
                st.session_state.manual_rows[i]["price"] = mprice

            manual_results.append(compute_manual(mname, mlots, mnop_m, mcs, mprice))

        if i < len(st.session_state.manual_rows) - 1:
            st.markdown("<hr style='border:none;border-top:1px solid #1e293b;margin:6px 0;'>",
                        unsafe_allow_html=True)

    # Only show results when at least one row has a price entered
    active_manual = [r for r in manual_results if r["Price"] > 0]
    if active_manual:
        st.markdown('<div class="sec-hdr">📊 Summary</div>', unsafe_allow_html=True)
        render_summary(active_manual)

        st.markdown('<div class="sec-hdr">🔍 Instrument Breakdown</div>', unsafe_allow_html=True)
        render_instrument_cards(active_manual)

        st.markdown('<div class="sec-hdr">📋 Risk Calculation Table</div>', unsafe_allow_html=True)
        st.markdown(render_risk_table(active_manual), unsafe_allow_html=True)

        st.markdown('<div class="sec-hdr">📥 Export</div>', unsafe_allow_html=True)
        mdf = pd.DataFrame(active_manual)[[
            "Symbol", "Contract Size", "Price", "Open Lots", "Direction",
            "NOP Limit (USD)", "Notional/Lot", "NOP Max Lots", "Current Exposure",
            "Remaining Lots", "PnL per $1", "Utilization %", "Margin/Lot @100x",
        ]]
        try:
            mbuf = io.BytesIO()
            with pd.ExcelWriter(mbuf, engine="openpyxl") as writer:
                mdf.to_excel(writer, sheet_name="Manual NOP Entry", index=False)
            mbuf.seek(0)
            me1, me2, _ = st.columns([1, 1, 3])
            with me1:
                st.download_button("📥 Download Excel", data=mbuf,
                    file_name=f"Manual_NOP_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with me2:
                st.download_button("📄 Download CSV", data=mdf.to_csv(index=False),
                    file_name=f"Manual_NOP_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv", use_container_width=True)
        except Exception:
            st.download_button("📄 Download CSV", data=mdf.to_csv(index=False),
                file_name=f"Manual_NOP_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv")
    else:
        st.info("Enter a price for at least one row to see calculations.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:14px 0;">
    <span style="color:#64748b;font-size:12px;">
    NOP Calculator v3.2 &nbsp;·&nbsp; Built for dealing desks
    </span>
</div>
""", unsafe_allow_html=True)
