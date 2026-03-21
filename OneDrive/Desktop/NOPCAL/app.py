"""
Broker NOP Risk Dashboard — v2.0
Real-time Net Open Position monitoring for dealing desks.
Tracks metals (Gold, Silver) and indices (DJ30, NAS100, S&P500).

Deploy: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NOP Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme / CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Root ────────────────────────────────────── */
:root {
    --bg-primary: #0a0e17;
    --bg-card: #111827;
    --bg-card-hover: #1a2235;
    --border: #1e293b;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --accent-purple: #8b5cf6;
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --text-dim: #64748b;
}

html, body, [data-testid="stApp"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Header strip ────────────────────────────── */
.dash-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid var(--border);
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
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-purple));
}
.dash-header h1 {
    font-family: 'DM Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #f8fafc;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}
.dash-header p {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Summary cards ───────────────────────────── */
.summary-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 24px;
    text-align: left;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.summary-card:hover { border-color: var(--accent-blue); }
.summary-card .label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-dim);
    margin-bottom: 10px;
}
.summary-card .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.1;
}
.summary-card .sub {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 6px;
}
.card-blue   .value { color: var(--accent-blue); }
.card-green  .value { color: var(--accent-green); }
.card-amber  .value { color: var(--accent-amber); }
.card-red    .value { color: var(--accent-red); }
.card-purple .value { color: var(--accent-purple); }
.card-cyan   .value { color: var(--accent-cyan); }

/* ── Instrument cards ────────────────────────── */
.inst-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    transition: all 0.2s ease;
}
.inst-card:hover { transform: translateY(-2px); border-color: var(--accent-blue); box-shadow: 0 8px 24px rgba(59,130,246,0.08); }
.inst-card .sym { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 16px; color: var(--text-primary); }
.inst-card .dir-long  { color: var(--accent-green); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.inst-card .dir-short { color: var(--accent-red);   font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.inst-card .dir-flat  { color: var(--text-dim);     font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.inst-card .lots { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; margin: 8px 0; }
.inst-card .expo { font-size: 12px; color: var(--text-muted); }
.inst-card .bar-bg { background: #1e293b; border-radius: 6px; height: 8px; margin-top: 14px; overflow: hidden; }
.inst-card .bar-fill { height: 100%; border-radius: 6px; transition: width 0.4s ease; }
.inst-card .bar-label { font-size: 11px; color: var(--text-dim); margin-top: 6px; display: flex; justify-content: space-between; }

/* ── Risk table ──────────────────────────────── */
.risk-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-safe    { background: rgba(16,185,129,0.15); color: var(--accent-green); }
.badge-warning { background: rgba(245,158,11,0.15); color: var(--accent-amber); }
.badge-breach  { background: rgba(239,68,68,0.15);  color: var(--accent-red); }

/* ── Section headers ─────────────────────────── */
.section-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 32px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    letter-spacing: -0.3px;
}

/* ── Formula reference ───────────────────────── */
.formula-box {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid #2d2b55;
    border-radius: 12px;
    padding: 20px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 2;
    color: #c4b5fd;
}
.formula-box span { color: var(--accent-cyan); }

/* ── Misc ────────────────────────────────────── */
.stDataFrame { border-radius: 12px !important; }
div[data-testid="stMetric"] { background: var(--bg-card); border-radius: 10px; padding: 14px; border: 1px solid var(--border); }
div[data-testid="stMetric"] label { color: var(--text-dim) !important; text-transform: uppercase; font-size: 11px !important; letter-spacing: 1px; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; }

/* ── Sidebar ─────────────────────────────────── */
section[data-testid="stSidebar"] { background: #0f1629 !important; }
section[data-testid="stSidebar"] .stMarkdown h2 { color: var(--text-primary); font-size: 15px; }

/* ── Hide anchor links ───────────────────────── */
a.anchor-link { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSTRUMENT CONFIG
# ══════════════════════════════════════════════════════════════════════════════
INSTRUMENTS = {
    "XAUUSD": {
        "name": "Gold",
        "contract_size": 100,
        "yahoo": "GC=F",
        "default_price": 4500.00,
        "category": "Metals",
    },
    "XAGUSD": {
        "name": "Silver",
        "contract_size": 5000,
        "yahoo": "SI=F",
        "default_price": 68.00,
        "category": "Metals",
    },
    "US30": {
        "name": "DJ30",
        "contract_size": 1,
        "yahoo": "^DJI",
        "default_price": 45577.00,
        "category": "Indices",
    },
    "US100": {
        "name": "NAS100",
        "contract_size": 1,
        "yahoo": "^NDX",
        "default_price": 21648.00,
        "category": "Indices",
    },
    "US500": {
        "name": "S&P500",
        "contract_size": 1,
        "yahoo": "^GSPC",
        "default_price": 6506.00,
        "category": "Indices",
    },
}

NOP_OPTIONS = {
    "10M": 10_000_000,
    "50M": 50_000_000,
    "100M": 100_000_000,
    "200M": 200_000_000,
    "Custom": 0,
}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}
if "fetch_ts" not in st.session_state:
    st.session_state.fetch_ts = None
if "rows" not in st.session_state:
    st.session_state.rows = [
        {"symbol": "XAUUSD", "nop_preset": "100M", "nop_custom": 100_000_000, "open_lots": 0.0, "price_override": 0.0},
        {"symbol": "XAGUSD", "nop_preset": "10M",  "nop_custom": 10_000_000,  "open_lots": 0.0, "price_override": 0.0},
        {"symbol": "US30",   "nop_preset": "100M", "nop_custom": 100_000_000, "open_lots": 0.0, "price_override": 0.0},
        {"symbol": "US100",  "nop_preset": "100M", "nop_custom": 100_000_000, "open_lots": 0.0, "price_override": 0.0},
        {"symbol": "US500",  "nop_preset": "100M", "nop_custom": 100_000_000, "open_lots": 0.0, "price_override": 0.0},
    ]


# ══════════════════════════════════════════════════════════════════════════════
# PRICE FETCHER
# ══════════════════════════════════════════════════════════════════════════════
def fetch_prices():
    """Fetch live prices using yfinance. Returns dict of symbol->price."""
    fetched = {}
    try:
        import yfinance as yf
        yahoo_map = {v["yahoo"]: k for k, v in INSTRUMENTS.items()}
        tickers_str = " ".join(v["yahoo"] for v in INSTRUMENTS.values())
        data = yf.download(tickers_str, period="1d", group_by="ticker", progress=False)
        for yahoo_sym, local_sym in yahoo_map.items():
            try:
                if len(INSTRUMENTS) == 1:
                    close = data["Close"].iloc[-1]
                else:
                    close = data[yahoo_sym]["Close"].iloc[-1]
                if pd.notna(close) and close > 0:
                    fetched[local_sym] = round(float(close), 2)
            except Exception:
                pass
        # Fallback: individual fetch for missing symbols
        for sym, cfg in INSTRUMENTS.items():
            if sym not in fetched:
                try:
                    t = yf.Ticker(cfg["yahoo"])
                    hist = t.history(period="5d")
                    if not hist.empty:
                        fetched[sym] = round(float(hist["Close"].iloc[-1]), 2)
                except Exception:
                    pass
    except ImportError:
        pass
    return fetched


def get_price(symbol):
    """Get price: live > override > default."""
    cfg = INSTRUMENTS[symbol]
    if symbol in st.session_state.live_prices:
        return st.session_state.live_prices[symbol]
    return cfg["default_price"]


# ══════════════════════════════════════════════════════════════════════════════
# CALCULATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def compute_row(symbol, open_lots, nop_limit_usd, price_override=0.0):
    """Compute all risk metrics for a single instrument row."""
    cfg = INSTRUMENTS[symbol]
    price = price_override if price_override > 0 else get_price(symbol)
    cs = cfg["contract_size"]
    notional = price * cs
    nop_max = notional and nop_limit_usd / notional or 0
    exposure = abs(open_lots) * notional
    remaining = nop_max - abs(open_lots)
    pnl_per_1 = abs(open_lots) * cs
    utilization = (exposure / nop_limit_usd * 100) if nop_limit_usd > 0 else 0
    margin_100 = notional / 100 if notional else 0  # leverage 100
    direction = "NET LONG" if open_lots > 0 else ("NET SHORT" if open_lots < 0 else "FLAT")
    return {
        "Symbol": symbol,
        "Name": cfg["name"],
        "Category": cfg["category"],
        "Contract Size": cs,
        "Price": price,
        "Open Lots": open_lots,
        "Direction": direction,
        "Notional/Lot": notional,
        "NOP Limit (USD)": nop_limit_usd,
        "NOP Max Lots": round(nop_max, 2),
        "Current Exposure": exposure,
        "Remaining Lots": round(remaining, 2),
        "PnL per $1": pnl_per_1,
        "Utilization %": round(utilization, 2),
        "Margin/Lot @100x": margin_100,
    }


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
    <h1>🛡️ Broker NOP Risk Dashboard</h1>
    <p>Net Open Position &nbsp;·&nbsp; Notional Exposure &nbsp;·&nbsp; Capacity Monitor &nbsp;·&nbsp; Dealing Desk RMS</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    # Fetch button
    if st.button("🔄 Fetch Live Prices", use_container_width=True, type="primary"):
        with st.spinner("Connecting to markets…"):
            prices = fetch_prices()
            if prices:
                st.session_state.live_prices.update(prices)
                st.session_state.fetch_ts = datetime.now().strftime("%H:%M:%S")
                st.success(f"Fetched {len(prices)} prices")
            else:
                st.warning("API unavailable — using defaults / manual")

    if st.session_state.fetch_ts:
        st.caption(f"Last fetch: {st.session_state.fetch_ts}")

    # Show current prices
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
    st.markdown("### 📋 Contract Sizes")
    for sym, cfg in INSTRUMENTS.items():
        unit = "oz" if cfg["category"] == "Metals" else "unit"
        st.markdown(f"`{sym}` → **{cfg['contract_size']:,}** {unit}")

    st.markdown("---")
    st.caption("v2.0 · Streamlit Cloud Ready")


# ══════════════════════════════════════════════════════════════════════════════
# POSITION INPUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📝 Position & Limit Inputs</div>', unsafe_allow_html=True)
st.caption("Configure each instrument: select symbol, set NOP limit, enter net open lots (positive = long, negative = short). Override price if needed.")

# Row management
col_add, col_remove, _ = st.columns([1, 1, 4])
with col_add:
    if st.button("➕ Add Row", use_container_width=True):
        st.session_state.rows.append({
            "symbol": "XAUUSD", "nop_preset": "100M",
            "nop_custom": 100_000_000, "open_lots": 0.0, "price_override": 0.0,
        })
        st.rerun()
with col_remove:
    if len(st.session_state.rows) > 1:
        if st.button("➖ Remove Last", use_container_width=True):
            st.session_state.rows.pop()
            st.rerun()

symbol_options = list(INSTRUMENTS.keys())
nop_labels = list(NOP_OPTIONS.keys())

results = []

for i, row in enumerate(st.session_state.rows):
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1, 1.2])
        with c1:
            sym = st.selectbox(
                "Symbol", symbol_options,
                index=symbol_options.index(row["symbol"]) if row["symbol"] in symbol_options else 0,
                key=f"sym_{i}",
            )
            st.session_state.rows[i]["symbol"] = sym
        with c2:
            nop_choice = st.selectbox(
                "NOP Limit", nop_labels,
                index=nop_labels.index(row.get("nop_preset", "100M")),
                key=f"nop_{i}",
            )
            st.session_state.rows[i]["nop_preset"] = nop_choice
            if nop_choice == "Custom":
                nop_usd = st.number_input(
                    "Custom (USD)", value=int(row.get("nop_custom", 100_000_000)),
                    min_value=0, step=1_000_000, key=f"nop_c_{i}",
                )
                st.session_state.rows[i]["nop_custom"] = nop_usd
            else:
                nop_usd = NOP_OPTIONS[nop_choice]
                st.session_state.rows[i]["nop_custom"] = nop_usd
        with c3:
            lots = st.number_input(
                "Open Lots (net)", value=row.get("open_lots", 0.0),
                step=0.01, format="%.2f", key=f"lots_{i}",
                help="+ve = Long, -ve = Short",
            )
            st.session_state.rows[i]["open_lots"] = lots
        with c4:
            cs = INSTRUMENTS[sym]["contract_size"]
            st.text_input("Contract Size", value=f"{cs:,}", disabled=True, key=f"cs_{i}")
        with c5:
            p_over = st.number_input(
                "Price Override", value=row.get("price_override", 0.0),
                min_value=0.0, step=0.01, format="%.2f", key=f"po_{i}",
                help="0 = use live/default price",
            )
            st.session_state.rows[i]["price_override"] = p_over

        results.append(compute_row(sym, lots, nop_usd, p_over))

    if i < len(st.session_state.rows) - 1:
        st.markdown("<hr style='border:none;border-top:1px solid #1e293b;margin:8px 0;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(results)

total_exposure = df["Current Exposure"].sum()
total_lots = df["Open Lots"].sum()
total_pnl1 = df["PnL per $1"].sum()
avg_util = df["Utilization %"].mean()
breach_count = (df["Remaining Lots"] < 0).sum()
active_count = (df["Open Lots"].abs() > 0).sum()

st.markdown('<div class="section-header">📊 Portfolio Summary</div>', unsafe_allow_html=True)

cols = st.columns(6)
cards = [
    ("TOTAL EXPOSURE",     f"${total_exposure:,.0f}",           f"{total_exposure/1e6:.1f}M USD",   "card-blue"),
    ("NET OPEN LOTS",      f"{total_lots:,.2f}",                "Across all instruments",           "card-cyan"),
    ("PnL PER $1 MOVE",    f"${total_pnl1:,.0f}",              "Portfolio sensitivity",            "card-purple"),
    ("AVG UTILIZATION",    f"{avg_util:.1f}%",                  "Of NOP limits",                    "card-amber" if avg_util > 40 else "card-green"),
    ("RISK BREACHES",      f"{breach_count}",                   "Remaining < 0",                    "card-red" if breach_count > 0 else "card-green"),
    ("ACTIVE INSTRUMENTS", f"{active_count}/{len(results)}",    "With open positions",              "card-cyan"),
]

for col, (label, value, sub, cls) in zip(cols, cards):
    with col:
        st.markdown(f"""
        <div class="summary-card {cls}">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INSTRUMENT DETAIL CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🔍 Instrument Breakdown</div>', unsafe_allow_html=True)

card_cols = st.columns(min(len(results), 5))
for idx, row_data in enumerate(results):
    col = card_cols[idx % len(card_cols)]
    with col:
        direction = row_data["Direction"]
        dir_class = "dir-long" if "LONG" in direction else ("dir-short" if "SHORT" in direction else "dir-flat")
        lots_color = "#10b981" if row_data["Open Lots"] > 0 else ("#ef4444" if row_data["Open Lots"] < 0 else "#64748b")

        util = row_data["Utilization %"]
        bar_color = "#ef4444" if util > 80 else ("#f59e0b" if util > 50 else "#10b981")
        bar_width = min(util, 100)

        status_class = "badge-breach" if row_data["Remaining Lots"] < 0 else ("badge-warning" if util > 70 else "badge-safe")
        status_text = "BREACH" if row_data["Remaining Lots"] < 0 else ("WARNING" if util > 70 else "SAFE")

        st.markdown(f"""
        <div class="inst-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span class="sym">{row_data['Symbol']}</span>
                <span class="risk-badge {status_class}">{status_text}</span>
            </div>
            <div class="{dir_class}" style="margin-top:6px;">{direction}</div>
            <div class="lots" style="color:{lots_color};">{row_data['Open Lots']:,.2f} <span style="font-size:14px;color:#64748b;">lots</span></div>
            <div class="expo">Exposure: ${row_data['Current Exposure']:,.0f}</div>
            <div class="expo">Notional/Lot: ${row_data['Notional/Lot']:,.0f}</div>
            <div class="expo">PnL per $1: ${row_data['PnL per $1']:,.0f}</div>
            <div class="bar-bg"><div class="bar-fill" style="width:{bar_width}%;background:{bar_color};"></div></div>
            <div class="bar-label">
                <span>Util: {util:.1f}%</span>
                <span>Max: {row_data['NOP Max Lots']:,.1f} lots</span>
            </div>
            <div class="expo" style="margin-top:6px;">Remaining: <b style="color:{'#ef4444' if row_data['Remaining Lots']<0 else '#10b981'}">{row_data['Remaining Lots']:,.2f}</b> lots</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FULL RESULTS TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📋 Full Risk Calculation Table</div>', unsafe_allow_html=True)

display_df = df[[
    "Symbol", "Name", "Direction", "Price", "Contract Size", "Open Lots",
    "Notional/Lot", "NOP Limit (USD)", "NOP Max Lots", "Current Exposure",
    "Remaining Lots", "PnL per $1", "Utilization %", "Margin/Lot @100x",
]].copy()


def highlight_risk(row):
    """Apply conditional formatting to risk table rows."""
    styles = [""] * len(row)
    if row["Remaining Lots"] < 0:
        styles = ["background-color: rgba(239,68,68,0.12); color: #fca5a5;"] * len(row)
    elif row["Utilization %"] > 70:
        styles = ["background-color: rgba(245,158,11,0.08); color: #fcd34d;"] * len(row)
    return styles


styled = display_df.style.apply(highlight_risk, axis=1).format({
    "Price": "${:,.2f}",
    "Contract Size": "{:,}",
    "Open Lots": "{:,.2f}",
    "Notional/Lot": "${:,.0f}",
    "NOP Limit (USD)": "${:,.0f}",
    "NOP Max Lots": "{:,.2f}",
    "Current Exposure": "${:,.0f}",
    "Remaining Lots": "{:,.2f}",
    "PnL per $1": "${:,.0f}",
    "Utilization %": "{:.1f}%",
    "Margin/Lot @100x": "${:,.2f}",
})

st.dataframe(styled, use_container_width=True, hide_index=True, height=280)


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">⚡ PnL Scenario Analysis</div>', unsafe_allow_html=True)
st.caption("What happens if the market moves?")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    move_gold = st.number_input("Gold move ($)", value=10.0, step=1.0, key="mv_g")
with sc2:
    move_silver = st.number_input("Silver move ($)", value=1.0, step=0.10, key="mv_s")
with sc3:
    move_index = st.number_input("Index move (pts)", value=100.0, step=10.0, key="mv_i")

scenario_rows = []
for r in results:
    cat = INSTRUMENTS[r["Symbol"]]["category"]
    if r["Symbol"] == "XAUUSD":
        mv = move_gold
    elif r["Symbol"] == "XAGUSD":
        mv = move_silver
    else:
        mv = move_index
    pnl = r["Open Lots"] * r["Contract Size"] * mv
    scenario_rows.append({
        "Symbol": r["Symbol"],
        "Name": r["Name"],
        "Net Lots": r["Open Lots"],
        "Contract Size": r["Contract Size"],
        "Price Move": mv,
        "PnL Impact ($)": pnl,
    })

sc_df = pd.DataFrame(scenario_rows)
st.dataframe(
    sc_df.style.format({
        "Net Lots": "{:,.2f}",
        "Contract Size": "{:,}",
        "Price Move": "${:,.2f}",
        "PnL Impact ($)": "${:,.0f}",
    }).applymap(
        lambda v: "color: #10b981; font-weight: 600" if isinstance(v, (int, float)) and v > 0 else
                  ("color: #ef4444; font-weight: 600" if isinstance(v, (int, float)) and v < 0 else ""),
        subset=["PnL Impact ($)"],
    ),
    use_container_width=True, hide_index=True,
)

total_pnl_sc = sc_df["PnL Impact ($)"].sum()
pnl_color = "#10b981" if total_pnl_sc >= 0 else "#ef4444"
st.markdown(f"""
<div class="summary-card" style="max-width:360px;margin-top:12px;">
    <div class="label">TOTAL PORTFOLIO PnL IMPACT</div>
    <div class="value" style="color:{pnl_color};font-size:32px;">${total_pnl_sc:,.0f}</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL EXPORT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📥 Export</div>', unsafe_allow_html=True)

export_df = df[[
    "Symbol", "Name", "Contract Size", "Price", "Open Lots", "Direction",
    "NOP Limit (USD)", "Notional/Lot", "NOP Max Lots", "Current Exposure",
    "Remaining Lots", "PnL per $1", "Utilization %", "Margin/Lot @100x",
]].copy()

# Excel export
try:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, sheet_name="NOP Risk Report", index=False)
        sc_df.to_excel(writer, sheet_name="Scenario Analysis", index=False)
    buffer.seek(0)

    exp1, exp2, _ = st.columns([1, 1, 3])
    with exp1:
        st.download_button(
            "📥 Download Excel (.xlsx)",
            data=buffer,
            file_name=f"NOP_Risk_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with exp2:
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV",
            data=csv_data,
            file_name=f"NOP_Risk_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
except Exception:
    csv_data = export_df.to_csv(index=False)
    st.download_button(
        "📄 Download CSV",
        data=csv_data,
        file_name=f"NOP_Risk_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:16px 0;">
    <span style="color:#64748b;font-size:12px;">
    Broker NOP Risk Dashboard v2.0 &nbsp;·&nbsp;
    Notional = Price × Contract Size &nbsp;·&nbsp;
    NOP Max = Limit ÷ Notional &nbsp;·&nbsp;
    Remaining = Max − |Open Lots| &nbsp;·&nbsp;
    Built for dealing desks
    </span>
</div>
""", unsafe_allow_html=True)
