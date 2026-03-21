# Broker NOP Risk Dashboard

Real-time Net Open Position monitoring for dealing desks.
Tracks Gold, Silver, DJ30, NAS100, S&P500.

---

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (Free)

### Step 1 — Push to GitHub
Create a new repo and push these files:
```
your-repo/
├── app.py
├── requirements.txt
└── README.md
```

### Step 2 — Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo, branch `main`, file `app.py`
5. Click **Deploy**

Your app will be live at `https://your-app.streamlit.app` within minutes.

---

## What It Does

| Feature | Description |
|---------|-------------|
| **Symbol Selection** | Dropdown: XAUUSD, XAGUSD, US30, US100, US500 |
| **NOP Limits** | Preset 10M / 50M / 100M / 200M or custom |
| **Live Prices** | Fetches via yfinance with manual override |
| **Risk Calc** | Notional, Max Lots, Remaining, Utilization |
| **Visual Alerts** | RED = breach, AMBER = warning, GREEN = safe |
| **Scenario** | PnL impact for price moves |
| **Export** | Excel (.xlsx) and CSV download |

---

## Formulas

```
Notional/Lot    = Price x Contract Size
NOP Max Lots    = NOP Limit (USD) / Notional per Lot
Current Exposure = |Open Lots| x Notional per Lot
Remaining Lots  = NOP Max Lots - |Open Lots|
PnL per $1      = |Open Lots| x Contract Size
Utilization %   = Current Exposure / NOP Limit x 100
```

## Contract Sizes (MT5 Standard)

| Symbol | Size | Unit |
|--------|------|------|
| XAUUSD | 100 | oz |
| XAGUSD | 5,000 | oz |
| US30 | 1 | index unit |
| US100 | 1 | index unit |
| US500 | 1 | index unit |

---

## License

Internal use. Built for dealing desk risk monitoring.
