"""
Crypto Tokenomics Analyzer & Rating Engine - Streamlit Web Application
Institutional Metric-Driven Tokenomics Rating System & Deep Fundamental Research Platform
"""

import sys
import streamlit as st

# Auto-bootstrap Streamlit when executed directly via `python app.py`
if __name__ == "__main__" and not st.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", sys.argv[0], "--server.address=127.0.0.1"]
    sys.exit(stcli.main())

import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime

import api_service
import scoring
import token_db
import importlib
importlib.reload(api_service)
importlib.reload(scoring)
importlib.reload(token_db)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Crypto Tokenomics Analyzer & Research Engine",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------
# ---------------------------------------------------------
# Custom 2027 Cyber-Institutional Styling & Visual Themes
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&family=Orbitron:wght@600;700;800;900&display=swap');

    /* Global Ambient Background & Canvas */
    .stApp {
        background: radial-gradient(circle at 12% 10%, rgba(0, 242, 254, 0.04) 0%, transparent 40%),
                    radial-gradient(circle at 88% 15%, rgba(121, 40, 202, 0.05) 0%, transparent 45%),
                    radial-gradient(circle at 50% 90%, rgba(0, 255, 135, 0.02) 0%, transparent 50%),
                    #07090e;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Futuristic Header Banner & Ticker Ribbon */
    .cyber-ticker {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, rgba(15, 23, 42, 0.85) 0%, rgba(13, 17, 28, 0.95) 50%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(0, 242, 254, 0.22);
        border-radius: 12px;
        padding: 9px 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
    }
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff87;
        box-shadow: 0 0 12px #00ff87, 0 0 4px #00ff87;
        margin-right: 8px;
        animation: pulseBeacon 2.2s infinite ease-in-out;
    }
    @keyframes pulseBeacon {
        0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 12px #00ff87; }
        50% { transform: scale(1.35); opacity: 0.75; box-shadow: 0 0 20px #00ff87; }
    }
    .ticker-tag {
        font-family: 'Orbitron', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: #00f2fe;
        text-transform: uppercase;
    }
    .ticker-item {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #94a3b8;
    }

    /* Metric Box (2027 Glassmorphism) */
    .metric-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0.008) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 2px solid rgba(0, 242, 254, 0.45);
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        margin-bottom: 12px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 242, 254, 0.6);
        box-shadow: 0 12px 30px rgba(0, 242, 254, 0.12);
    }
    .metric-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.76rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }
    .metric-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Financial Multiples Box (Neon Blue/Violet) */
    .fin-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(121, 40, 202, 0.04) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-top: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        margin-bottom: 12px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
        transition: all 0.25s ease;
    }
    .fin-box:hover {
        transform: translateY(-2px);
        border-color: #60a5fa;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.22);
    }

    /* Risk & Accrual Badges */
    .risk-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.16);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.45);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.15);
    }
    .badge-blue {
        background: rgba(59, 130, 246, 0.16);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.45);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.15);
    }
    .badge-orange {
        background: rgba(249, 115, 22, 0.16);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.45);
        box-shadow: 0 0 12px rgba(249, 115, 22, 0.15);
    }
    .badge-red {
        background: rgba(239, 68, 68, 0.16);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.45);
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.15);
    }
    .badge-purple {
        background: rgba(168, 85, 247, 0.16);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.45);
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.15);
    }
    .badge-cyan {
        background: rgba(0, 242, 254, 0.16);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.45);
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.15);
    }

    /* Vector Card (Institutional Vector Engine) */
    .vector-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.008) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 11px;
        backdrop-filter: blur(14px);
        transition: all 0.22s ease;
    }
    .vector-card:hover {
        border-color: rgba(0, 242, 254, 0.35);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.08);
        transform: translateX(2px);
    }
    .vector-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .vector-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.98rem;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: -0.01em;
    }
    .vector-score {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 6px;
    }
    .vector-driver {
        font-family: 'Inter', sans-serif;
        font-size: 0.84rem;
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .vector-evidence {
        font-family: 'Inter', sans-serif;
        font-size: 0.80rem;
        color: #94a3b8;
        line-height: 1.4;
    }

    /* Holographic Grade Banner */
    .holo-grade-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    .holo-grade-card::after {
        content: '';
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: linear-gradient(135deg, transparent 40%, rgba(255, 255, 255, 0.03) 50%, transparent 60%);
        pointer-events: none;
    }

    /* Modern Streamlit Tab Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 8px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        color: #94a3b8;
        padding: 0 12px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(59, 130, 246, 0.12) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        box-shadow: 0 2px 10px rgba(0, 242, 254, 0.15);
    }

    /* Cyber Ribbon Button Styling */
    div[data-testid="column"] button {
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] button:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Helper Functions: 2027 Visual Figures & Gauges
# ---------------------------------------------------------
def create_2027_radial_gauge(score, grade_info):
    """Generates an institutional 2027 radial safety gauge with glowing thresholds."""
    grade = grade_info.get("grade", "BBB")
    color = grade_info.get("color", "#3b82f6")
    verdict = grade_info.get("verdict", "Moderate Risk")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "suffix": " / 10",
            "font": {"size": 36, "family": "Space Grotesk, sans-serif", "color": "#f8fafc"},
            "valueformat": ".2f"
        },
        title={
            "text": f"<span style='font-size:0.78em;letter-spacing:0.12em;color:#94a3b8;font-family:Orbitron;'>INSTITUTIONAL SAFETY MATRIX</span><br><b style='color:{color};font-size:1.35em;font-family:Space Grotesk;'>GRADE {grade}</b> <span style='font-size:0.80em;color:#cbd5e1;'>({verdict})</span>",
            "font": {"size": 15}
        },
        gauge={
            "axis": {
                "range": [0, 10],
                "tickwidth": 1,
                "tickcolor": "rgba(255,255,255,0.25)",
                "tickvals": [0, 2, 4, 6, 8, 10],
                "ticktext": ["0", "2", "4", "6", "8", "10"],
                "tickfont": {"size": 11, "color": "#94a3b8", "family": "JetBrains Mono"}
            },
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 1,
            "bordercolor": "rgba(255,255,255,0.1)",
            "steps": [
                {"range": [0, 3.5], "color": "rgba(239, 68, 68, 0.16)"},
                {"range": [3.5, 5.5], "color": "rgba(249, 115, 22, 0.13)"},
                {"range": [5.5, 7.5], "color": "rgba(245, 158, 11, 0.13)"},
                {"range": [7.5, 8.8], "color": "rgba(0, 242, 254, 0.16)"},
                {"range": [8.8, 10.0], "color": "rgba(0, 255, 135, 0.20)"}
            ],
            "threshold": {
                "line": {"color": "#ffffff", "width": 3},
                "thickness": 0.8,
                "value": score
            }
        }
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=25, r=25, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"}
    )
    return fig


def apply_2027_theme(fig, height=None):
    """Applies institutional dark 2027 styling to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#e2e8f0"),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.12)",
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#94a3b8")
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.12)",
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#94a3b8")
        )
    )
    if height:
        fig.update_layout(height=height)
    return fig


# ---------------------------------------------------------
# State Management
# ---------------------------------------------------------
if "token_history" not in st.session_state:
    st.session_state.token_history = []

if "selected_coin_id" not in st.session_state:
    st.session_state.selected_coin_id = "makerdao"

if "manual_override" not in st.session_state:
    st.session_state.manual_override = False

# ---------------------------------------------------------
# Sidebar: Token Selection & Presets
# ---------------------------------------------------------
with st.sidebar:
    st.title("🪙 Tokenomics Research")
    st.caption("Cash-flow, buyback & safety rating engine.")

    st.subheader("⚡ Bellwether Presets")
    st.caption("Select protocols showcasing different tokenomics models:")

    presets = [
        ("MKR", "makerdao"),
        ("ETH", "ethereum"),
        ("BNB", "binancecoin"),
        ("GMX", "gmx"),
        ("HYPE", "hyperliquid"),
        ("UNI", "uniswap"),
        ("AAVE", "aave"),
        ("RAY", "raydium"),
        ("SOL", "solana"),
        ("BTC", "bitcoin"),
        ("TIA", "celestia"),
        ("SUI", "sui"),
        ("ARB", "arbitrum")
    ]
    
    cols_preset = st.columns(4)
    for idx, (sym, cid) in enumerate(presets):
        col = cols_preset[idx % 4]
        if col.button(sym, key=f"btn_{cid}", use_container_width=True):
            st.session_state.selected_coin_id = cid
            st.session_state.manual_override = False
            st.rerun()

    st.markdown("---")
    st.subheader("🔍 Search Tokens")
    search_query = st.text_input("Search (Name or Ticker):", placeholder="e.g. AAVE, Pendle, Lido")
    
    if search_query:
        search_results = api_service.search_tokens(search_query)
        if search_results:
            options = {f"{c['name']} ({c['symbol']}) - Rank #{c.get('market_cap_rank') or 'N/A'}": c['id'] for c in search_results}
            selected_label = st.selectbox("Select Result:", list(options.keys()))
            if selected_label:
                selected_id = options[selected_label]
                if st.button("Load Selected Token", use_container_width=True):
                    st.session_state.selected_coin_id = selected_id
                    st.session_state.manual_override = False
                    st.rerun()
        else:
            st.info("No matching tokens found.")

    st.markdown("---")
    
    # CoinGecko API Key Expander (Optional)
    with st.expander("🔑 CoinGecko API Key (Optional)", expanded=False):
        st.caption("No key required! If left empty, the app runs 100% on free public APIs (CoinPaprika & DeFiLlama). If you have a free CoinGecko Demo Key, enter it below:")
        current_k = st.session_state.get("coingecko_api_key", api_service.get_api_key())
        user_key = st.text_input("CoinGecko Key:", value=current_k, type="password", placeholder="CG-xxxxxxxx")
        if user_key != current_k:
            st.session_state.coingecko_api_key = user_key
            api_service.set_api_key(user_key)
            st.rerun()

    # Vector Weights Configuration Expander
    with st.expander("⚖️ Vector Weight Allocations", expanded=False):
        st.caption("Adjust weighting for institutional criteria (defaults to standard weights).")
        w1 = st.slider("Supply Dynamics & Float", 0.0, 1.0, scoring.DEFAULT_WEIGHTS["v1"], 0.05)
        w2 = st.slider("Utility & Demand Velocity", 0.0, 1.0, scoring.DEFAULT_WEIGHTS["v2"], 0.05)
        w3 = st.slider("Value Accrual & Cash Flow Safety", 0.0, 1.0, scoring.DEFAULT_WEIGHTS["v3"], 0.05)
        w4 = st.slider("Ecosystem Scale & Depth", 0.0, 1.0, scoring.DEFAULT_WEIGHTS["v4"], 0.05)
        w5 = st.slider("Solvency & Cliff Absorption", 0.0, 1.0, scoring.DEFAULT_WEIGHTS["v5"], 0.05)
        weights = {"v1": w1, "v2": w2, "v3": w3, "v4": w4, "v5": w5}
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {k: v / total_w for k, v in weights.items()}
    if "weights" not in locals():
        weights = scoring.DEFAULT_WEIGHTS

    # Rate Limit & Compliance Expander
    with st.expander("🛡️ Rate Limit & Compliance Monitor", expanded=False):
        c_stats = api_service.get_compliance_stats()
        cg = c_stats["coingecko"]
        cp = c_stats["coinpaprika"]
        cache = c_stats["cache"]

        st.caption("Active client-side rate limiters enforce upstream API compliance and prevent IP blocks.")
        
        if cg["in_cooldown"]:
            cg_badge = f"🟠 In Cooldown ({cg['cooldown_remaining']}s remaining)"
        else:
            cg_badge = f"🟢 Compliant ({cg['calls_last_minute']}/{cg['max_calls']} req/min)"
        st.markdown(f"- **CoinGecko**: {cg_badge}")
        st.markdown(f"- **CoinPaprika**: 🟢 Compliant ({cp['calls_last_minute']}/{cp['max_calls']} req/min)")
        st.markdown(f"- **Local Cache**: {cache['cached_entries']} entries ({cache['hits']} hits saved)")

    st.caption("Powered by CoinGecko, CoinPaprika & DeFiLlama Public APIs")

# ---------------------------------------------------------
# Data Retrieval & Metric Calculation
# ---------------------------------------------------------
market_data = None
token_display_name = "Custom Token"
token_symbol = "CUSTOM"
token_image = None

# 1. Fetch Local Curated Token Profile (Knowledge Store)
profile = token_db.get_profile(st.session_state.selected_coin_id)

with st.spinner(f"Fetching market tokenomics for '{st.session_state.selected_coin_id}'..."):
    market_data = api_service.fetch_token_market_data(st.session_state.selected_coin_id)
    if market_data:
        token_display_name = market_data.get("name", "Unknown Token")
        token_symbol = market_data.get("symbol", "TOKEN")
        token_image = market_data.get("image")

# 2. Fetch Live Protocol Financials (DeFiLlama Fees & Revenue)
slug = profile.get("defillama_slug") if profile else st.session_state.selected_coin_id
financials = None
if slug and market_data:
    financials = api_service.fetch_protocol_financials(slug, market_data.get("market_cap_usd", 0.0))

# 3. Fetch Live DAO Treasury Breakdown (DeFiLlama Treasury API)
treasury_slug = profile.get("treasury_details", {}).get("defillama_slug") if profile else ""
fallback_liq = profile.get("treasury_details", {}).get("liquid_stables_usd", 0.0) if profile else 0.0
fallback_nat = profile.get("treasury_details", {}).get("native_treasury_usd", 0.0) if profile else 0.0
treasury = api_service.fetch_dao_treasury(treasury_slug, fallback_liq, fallback_nat)

# 4. Fetch Order Book 2% Depth & Slippage Fragility
next_c_usd = profile.get("unlock_schedule", {}).get("next_cliff_usd", 0.0) if profile else 0.0
vol_24h = market_data.get("volume_24h_usd", 0.0) if market_data else 0.0
depth = api_service.fetch_market_depth_and_slippage(token_symbol, vol_24h, next_c_usd)

# 5. Compute Institutional Derived Metrics
inst_metrics = api_service.compute_institutional_derived_metrics(market_data, profile, financials, treasury, depth)

# 6. Compute Objective 5-Vector Scoring with Institutional Depth
if market_data:
    eval_result = scoring.compute_metric_driven_tokenomics(
        market_data,
        profile=profile,
        financials=financials,
        treasury=treasury,
        depth=depth,
        inst_metrics=inst_metrics
    )
else:
    eval_result = {
        "scores": {"v1": 5.0, "v2": 5.0, "v3": 5.0, "v4": 5.0, "v5": 5.0},
        "vector_details": {},
        "composite_score": 5.0,
        "grade_info": scoring.calculate_grade(5.0),
        "weights": weights,
        "accrual_label": "General Tokenomics",
        "warning_badges": [],
        "inst_metrics": {},
        "depth": {},
        "treasury": {}
    }

# ---------------------------------------------------------
# Cyber-Ticker Ribbon (2027 Live Telemetry)
# ---------------------------------------------------------
st.markdown("""
<div class='cyber-ticker'>
    <div style='display: flex; align-items: center;'>
        <span class='pulse-dot'></span>
        <span class='ticker-tag'>AURA // QUANT ENGINE 2027</span>
        <span style='margin: 0 12px; color: rgba(255, 255, 255, 0.15);'>|</span>
        <span class='ticker-item'>TELEMETRY: <b style='color: #00ff87;'>LIVE DECENTRALIZED PUBLIC</b></span>
    </div>
    <div style='display: flex; align-items: center; gap: 18px;'>
        <span class='ticker-item'>🛡️ <b>7-VECTOR AUDIT MATRIX</b></span>
        <span class='ticker-item'>🔥 <b>HARD BURNS & CASH FLOWS</b></span>
        <span class='ticker-item'>⚡ <b>ZERO-KEY COMPLIANT</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Quick-Audit Bellwether Ribbon (Instant 1-Click Switching)
# ---------------------------------------------------------
st.markdown("<div style='margin-bottom: 6px; font-size: 0.76rem; font-family: Space Grotesk; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 600;'>⚡ Quick Institutional Bellwether Audit:</div>", unsafe_allow_html=True)
q_cols = st.columns(8)
quick_presets = [
    ("🦄 UNI", "uniswap", "UNIfication Fee-Switch & Firepit Burn (AA)"),
    ("🟡 BNB", "binancecoin", "Auto-Burn & BEP-95 Deflation (AAA)"),
    ("🔷 ETH", "ethereum", "EIP-1559 Ultrasound Burn (AAA)"),
    ("🏦 MKR", "makerdao", "Smart Burn Engine & Buybacks (AA)"),
    ("📈 GMX", "gmx", "Real Yield Fee Redistribution (A)"),
    ("🔴 ARB", "arbitrum", "High Overhang & Sequencer Risk (C)"),
    ("🧊 TIA", "celestia", "VC Cliff & Predatory Dilution (D)"),
    ("⚡ SOL", "solana", "High Throughput Execution (A)")
]

for i, (q_sym, q_cid, q_tip) in enumerate(quick_presets):
    with q_cols[i]:
        is_active = (st.session_state.selected_coin_id == q_cid)
        btn_label = f"✨ {q_sym}" if is_active else q_sym
        if st.button(btn_label, key=f"qbtn_{q_cid}", use_container_width=True, help=q_tip):
            st.session_state.selected_coin_id = q_cid
            st.session_state.manual_override = False
            st.rerun()

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main UI Header & Accrual Architecture Badge
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

# Determine Accrual Badge Style
accrual_type = profile.get("value_accrual_type", "unknown") if profile else "unknown"
if accrual_type == "buyback_and_burn":
    badge_style = "badge-green"
    badge_text = "🔥 Active Buyback & Burn"
elif accrual_type in ["dual_burn_deflationary", "dual_burn"]:
    badge_style = "badge-green"
    badge_text = "🔥 Dual Deflationary Burn"
elif accrual_type == "fee_share_real_yield":
    badge_style = "badge-blue"
    badge_text = "💎 Real Yield Fee Sharing"
elif accrual_type == "gas_burn_deflationary":
    badge_style = "badge-purple"
    badge_text = "⚡ Deflationary Base Burn"
elif accrual_type == "fee_switch_dormant":
    badge_style = "badge-orange"
    badge_text = "⚠️ Dormant Fee Switch"
elif accrual_type == "staking_emissions_only":
    badge_style = "badge-orange"
    badge_text = "📉 Inflationary Staking Only"
elif accrual_type == "pure_governance_no_cashflow":
    badge_style = "badge-red"
    badge_text = "⛔ Pure Governance (No Cash Flow)"
else:
    badge_style = "badge-blue"
    badge_text = "Standard Utility"

with col_head1:
    reg_info = profile.get("regulatory_classification", {}) if profile else {}
    reg_tag = reg_info.get("tag", "🟢 Commodity / Low Regulatory Risk")
    reg_col = reg_info.get("color", "green")
    reg_badge_style = f"badge-{reg_col}" if reg_col in ["green", "orange", "red"] else "badge-blue"

    header_html = "<div style='display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 6px;'>"
    if token_image:
        header_html += f"<img src='{token_image}' width='46' height='46' style='border-radius: 50%; box-shadow: 0 0 16px rgba(0, 242, 254, 0.25); border: 1px solid rgba(255, 255, 255, 0.15);' />"
    header_html += f"<h1 style='margin: 0; font-family: Space Grotesk, sans-serif; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.02em;'>{token_display_name} <span style='color: #64748b; font-size: 1.35rem; font-family: JetBrains Mono, monospace;'>({token_symbol})</span></h1>"
    header_html += f"<span class='risk-badge {badge_style}' style='font-size: 0.85rem;'>{badge_text}</span>"
    header_html += f"<span class='risk-badge {reg_badge_style}' style='font-size: 0.85rem;'>{reg_tag}</span>"
    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Render Institutional Warning Alert Badges
    warning_badges = eval_result.get("warning_badges", [])
    if warning_badges:
        w_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 10px 0;'>"
        for wb in warning_badges:
            w_html += f"<span class='risk-badge {wb['style']}' title='{wb.get('tooltip', '')}'>{wb['text']}</span>"
        w_html += "</div>"
        st.markdown(w_html, unsafe_allow_html=True)

    if profile and profile.get("value_accrual_headline"):
        st.markdown(f"**Value Accrual Summary:** *{profile['value_accrual_headline']}*")
    elif market_data:
        st.caption(market_data.get("description", ""))

with col_head2:
    if market_data:
        p_chg = market_data.get("price_change_24h_pct", 0.0)
        color_p = "#00ff87" if p_chg >= 0 else "#f87171"
        arrow = "▲" if p_chg >= 0 else "▼"
        st.markdown(f"""
        <div style='text-align: right; padding-top: 6px;'>
            <div style='font-family: Space Grotesk, sans-serif; font-size: 2.1rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;'>${market_data.get('price_usd', 0.0):,.4f}</div>
            <div style='color: {color_p}; font-family: JetBrains Mono, monospace; font-weight: 700; font-size: 0.95rem; margin-top: 2px;'>{arrow} {p_chg:+.2f}% (24h)</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Live Protocol Cash Flow & Valuation Multiples Row
# ---------------------------------------------------------
if financials and financials.get("has_fees"):
    st.markdown("### 💰 Protocol Cash Flow & Valuation Multiples (DeFiLlama Live)")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown(f"""
        <div class='fin-box'>
            <div class='metric-title'>24h Protocol Fees</div>
            <div class='metric-value'>${financials['fees_24h_usd']:,.0f}</div>
            <div class='metric-subtitle'>30d Fees: ${financials['fees_30d_usd']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown(f"""
        <div class='fin-box'>
            <div class='metric-title'>Annualized Fees (Run-Rate)</div>
            <div class='metric-value'>${financials['annualized_fees_usd']:,.0f}</div>
            <div class='metric-subtitle'>Gross Protocol Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        pf = financials.get('price_to_fees_ratio')
        pf_disp = f"{pf:.1f}x" if pf else "N/A"
        pf_badge = "badge-green" if (pf and pf < 20) else ("badge-blue" if (pf and pf < 50) else "badge-orange")
        st.markdown(f"""
        <div class='fin-box'>
            <div class='metric-title'>Price-to-Fees (P/F Multiple)</div>
            <div class='metric-value'>{pf_disp}</div>
            <div class='metric-subtitle'><span class='risk-badge {pf_badge}'>{'Deep Value' if (pf and pf < 20) else 'Fair Valuation'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        fy = financials.get('fee_yield_pct', 0.0)
        st.markdown(f"""
        <div class='fin-box'>
            <div class='metric-title'>Annual Fee Yield %</div>
            <div class='metric-value'>{fy:.2f}%</div>
            <div class='metric-subtitle'>Annualized Fees / Market Cap</div>
        </div>
        """, unsafe_allow_html=True)
elif profile and profile.get("value_accrual_type") in ["pure_governance_no_cashflow", "staking_emissions_only"]:
    st.info("ℹ️ **Zero Direct Cash Flow Notice**: This protocol currently generates negligible protocol fees or routes 100% of sequencer/DEX revenues away from tokenholders.")

# ---------------------------------------------------------
# Live Quantitative Market Fundamentals Row
# ---------------------------------------------------------
if market_data:
    st.markdown("### 📊 Objective Market Fundamentals")
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Market Cap</div>
            <div class='metric-value'>${market_data.get('market_cap_usd', 0.0):,.0f}</div>
            <div class='metric-subtitle'>Rank #{market_data.get('market_cap_rank') or 'N/A'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Fully Diluted (FDV)</div>
            <div class='metric-value'>${market_data.get('fdv_usd', 0.0):,.0f}</div>
            <div class='metric-subtitle'>24h Vol: ${market_data.get('volume_24h_usd', 0.0):,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        fr = market_data.get('float_ratio', 1.0)
        if fr >= 0.80: badge_class = "badge-green"
        elif fr >= 0.50: badge_class = "badge-blue"
        elif fr >= 0.25: badge_class = "badge-orange"
        else: badge_class = "badge-red"

        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Float Ratio (MC / FDV)</div>
            <div class='metric-value'>{fr:.2f}</div>
            <div class='metric-subtitle'><span class='risk-badge {badge_class}'>{market_data.get('dilution_risk_level', 'Moderate')}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        burn_s = market_data.get('burned_supply', 0.0)
        if burn_s > 0:
            circ_sub = f"🔥 {market_data.get('burned_pct', 0.0):.1f}% Burned ({burn_s:,.0f})"
        else:
            circ_sub = f"{market_data.get('circulating_pct', 100.0):.1f}% Unlocked"

        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Circulating Supply</div>
            <div class='metric-value'>{market_data.get('circulating_supply', 0.0):,.0f}</div>
            <div class='metric-subtitle'>{circ_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Turnover / Velocity</div>
            <div class='metric-value'>{market_data.get('turnover_pct', 0.0):.2f}%</div>
            <div class='metric-subtitle'>ATH Drawdown: {market_data.get('ath_change_pct', 0.0):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# Automated 5-Vector Scorecard & Evidence
# ---------------------------------------------------------
col_vectors, col_vis = st.columns([1, 1], gap="large")

with col_vectors:
    st.subheader("🎯 Institutional 5-Vector Scorecard")
    st.caption("Objective scores calculated from **cash flows, buyback programs, dilution overhang, and liquidity**.")

    scores = eval_result["scores"].copy()
    vector_details = eval_result["vector_details"]

    for vid, vmeta in scoring.VECTOR_METADATA.items():
        vinfo = vector_details.get(vid, {})
        vscore = vinfo.get("score", 5.0)
        vdriver = vinfo.get("headline", vmeta["name"])
        vevidence = vinfo.get("evidence", "")

        if vscore >= 8.5:
            sc_color = "#10b981"
            bg_badge = "rgba(16, 185, 129, 0.15)"
        elif vscore >= 7.0:
            sc_color = "#3b82f6"
            bg_badge = "rgba(59, 130, 246, 0.15)"
        elif vscore >= 5.0:
            sc_color = "#f59e0b"
            bg_badge = "rgba(245, 158, 11, 0.15)"
        elif vscore >= 3.0:
            sc_color = "#f97316"
            bg_badge = "rgba(249, 115, 22, 0.15)"
        else:
            sc_color = "#ef4444"
            bg_badge = "rgba(239, 68, 68, 0.15)"

        st.markdown(f"""
        <div class='vector-card'>
            <div class='vector-header'>
                <span class='vector-title'>{vmeta['name']}</span>
                <span class='vector-score' style='color: {sc_color}; background: {bg_badge}; border: 1px solid {sc_color};'>
                    {vscore:.1f} / 10.0
                </span>
            </div>
            <div class='vector-driver'>{vdriver}</div>
            <div class='vector-evidence'>{vevidence}</div>
        </div>
        """, unsafe_allow_html=True)

    # Optional Manual Override Accordion
    with st.expander("✏️ Need manual adjustments for unlisted / private tokens?", expanded=False):
        st.caption("You can manually override any vector score if analyzing an unlisted token:")
        st.session_state.manual_override = st.checkbox("Enable Manual Override", value=st.session_state.manual_override)
        if st.session_state.manual_override:
            for vid, vmeta in scoring.VECTOR_METADATA.items():
                scores[vid] = st.slider(f"Override: {vmeta['name']}", 0.0, 10.0, float(scores[vid]), 0.1, key=f"ov_{vid}")

# Re-compute composite score with configured weights
composite_score = scoring.compute_weighted_score(scores, weights)
grade_info = scoring.calculate_grade(composite_score)

# ---------------------------------------------------------
# Visual Analytics & Deep Research Tabs
# ---------------------------------------------------------
with col_vis:
    st.subheader("📈 Fundamental Safety Profile")

    # 2027 Institutional Radial Safety Gauge
    st.plotly_chart(create_2027_radial_gauge(composite_score, grade_info), use_container_width=True)

    # Holographic Grade & Verdict Summary Card
    st.markdown(f"""
    <div class='holo-grade-card' style='border-left: 5px solid {grade_info['color']}; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4), inset 0 0 20px {grade_info['color']}18;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center; gap: 14px;'>
                <div style='background: {grade_info['color']}22; border: 1.5px solid {grade_info['color']}; color: {grade_info['color']}; font-family: Orbitron, monospace; font-weight: 800; font-size: 1.5rem; padding: 4px 14px; border-radius: 8px; box-shadow: 0 0 16px {grade_info['color']}33;'>
                    {grade_info['grade']}
                </div>
                <div>
                    <div style='font-family: Orbitron, monospace; font-size: 0.70rem; letter-spacing: 0.12em; color: #94a3b8; text-transform: uppercase;'>INSTITUTIONAL VERDICT</div>
                    <div style='font-family: Space Grotesk, sans-serif; font-weight: 700; color: {grade_info['color']}; font-size: 1.1rem;'>
                        {grade_info['verdict']}
                    </div>
                </div>
            </div>
            <div style='text-align: right;'>
                <span class='risk-badge' style='background: {grade_info['color']}18; color: {grade_info['color']}; border: 1px solid {grade_info['color']}55; font-family: JetBrains Mono, monospace; font-size: 0.82rem;'>
                    SCORE: {composite_score:.2f} / 10.0
                </span>
            </div>
        </div>
        <p style='margin-top: 12px; margin-bottom: 0; color: #cbd5e1; font-size: 0.88rem; line-height: 1.45; font-family: Inter, sans-serif;'>
            {grade_info['summary']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_yield, tab_margin, tab_treasury, tab_sim, tab_cliffs, tab_whales, tab_radar, tab_thesis = st.tabs([
        "💎 Real Yield",
        "⚖️ Net Margin",
        "🏦 Treasury",
        "📉 Dilution Sim",
        "⏳ Cliffs & Depth",
        "🐋 Whale Entities",
        "🕸️ Radar Profile",
        "⚖️ Regulatory & Thesis"
    ])

    # Tab 1: Real Staking Yield & Value Accrual
    with tab_yield:
        st.markdown("#### 💎 Real Staking Yield & Accrual Architecture")
        
        stk = profile.get("staking_details", {}) if profile else {}
        nominal_apr = float(inst_metrics.get("nominal_staking_apr_pct", 0.0))
        inf_rate = float(inst_metrics.get("net_inflation_rate_pct", 0.0))
        real_apr = float(inst_metrics.get("real_staking_apr_pct", 0.0))
        staked_ratio = float(stk.get("staking_ratio_pct", 0.0))

        col_y1, col_y2, col_y3, col_y4 = st.columns(4)
        with col_y1:
            st.metric("Nominal Staking APR", f"{nominal_apr:.2f}%" if stk.get("has_staking") else "None")
        with col_y2:
            st.metric("Net Supply Inflation", f"{inf_rate:.2f}%")
        with col_y3:
            st.metric(
                "Real Staking APR",
                f"{real_apr:+.2f}%" if stk.get("has_staking") else "N/A",
                delta=f"{real_apr:.2f}%" if stk.get("has_staking") else None,
                delta_color="normal" if real_apr >= 0 else "inverse"
            )
        with col_y4:
            st.metric("Staked Supply Ratio", f"{staked_ratio:.1f}%" if stk.get("has_staking") else "N/A")

        if stk.get("has_staking"):
            if real_apr > 0:
                st.success(f"✅ **Real Yield Accrual**: Real Staking APR is **{real_apr:+.2f}%** after accounting for **{inf_rate:.2f}%** net supply inflation. Stakers accumulate authentic purchasing power.")
            else:
                st.warning(f"⚠️ **Dilutionary Staking Trap**: Real Staking APR is **{real_apr:+.2f}%**! Staking yield ({nominal_apr:.2f}%) fails to beat supply inflation ({inf_rate:.2f}%). Staking is merely dilutive token emission.")
        else:
            if profile and profile.get("value_accrual_type") in ["buyback_and_burn", "gas_burn_deflationary", "dual_burn"]:
                st.info("ℹ️ **Deflationary Accrual Architecture**: Value is accrued directly to token holders via permanent fee burns and buybacks rather than native token staking.")
            else:
                st.info("ℹ️ No active staking program configured for this token profile.")

        st.markdown("---")
        st.markdown("**Accrual Mechanics & Cash Flow Details:**")
        if profile:
            st.markdown(f"- **Architecture:** `{profile.get('value_accrual_type')}`")
            st.markdown(f"- **Summary:** {profile.get('value_accrual_headline')}")
            
            # Revenue Streams
            st.markdown("**Active Protocol Revenue Streams:**")
            rev_streams = profile.get("revenue_sources", [])
            if rev_streams:
                st.markdown(" ".join([f"`{r}`" for r in rev_streams]))
            else:
                st.caption("No specific revenue streams documented.")

            # Buybacks
            bb = profile.get("buyback_details", {})
            has_bb = bb.get("has_buyback", False)
            st.markdown(f"**Token Buyback Program:** {'✅ Active' if has_bb else '❌ No Buybacks'}")
            if has_bb:
                st.info(f"**Mechanism:** {bb.get('mechanism', 'N/A')}\n\n**Run-rate / Scale:** {bb.get('annual_burn_runrate_est', 'N/A')}")

            # Fee Switch
            fs = profile.get("fee_switch_details", {})
            st.markdown(f"**Fee Switch Status:** {'🟢 Active' if fs.get('is_active') else ('🟠 Available / Dormant' if fs.get('has_fee_switch') else '❌ None')}")
            if fs.get("description"):
                st.caption(fs.get("description"))

    # Tab 2: Net Protocol Margin & Mercenary Capital Test
    with tab_margin:
        st.markdown("#### ⚖️ Net Protocol Margin & Mercenary Capital Test")
        st.caption("Evaluate whether the protocol is genuinely profitable or relies on dilutive token emissions to subsidize user activity.")

        ann_fees = float(inst_metrics.get("annualized_fees_usd", 0.0))
        ann_inc = float(inst_metrics.get("annual_incentives_usd", 0.0))
        net_inc = float(inst_metrics.get("net_protocol_income_usd", 0.0))
        net_margin = float(inst_metrics.get("net_margin_pct", 0.0))
        is_mercenary = inst_metrics.get("is_mercenary_subsidized", False)

        cm1, cm2, cm3 = st.columns(3)
        with cm1:
            st.metric("Annualized Gross Fees", f"${ann_fees:,.0f}" if ann_fees > 0 else "N/A")
        with cm2:
            st.metric("Annual Token Emissions / Subsidies", f"${ann_inc:,.0f}" if ann_inc > 0 else "$0")
        with cm3:
            st.metric(
                "Net Protocol Operating Income",
                f"${net_inc:,.0f}",
                delta=f"{net_margin:.1f}% Margin",
                delta_color="normal" if net_inc >= 0 else "inverse"
            )

        if is_mercenary or net_inc < 0:
            st.error(f"⚠️ **Mercenary Capital Alert**: Protocol runs at an annual operating deficit of **${abs(net_inc):,.0f}** ({net_margin:.1f}% margin). Activity is heavily subsidized by token inflation; liquidity and users may exit if emissions decline.")
        elif ann_fees > 0:
            st.success(f"✅ **Self-Sustaining Protocol Cash Flows**: Protocol generates positive net operating income of **${net_inc:,.0f}** ({net_margin:.1f}% margin) after all token emissions.")
        else:
            st.info("ℹ️ Minimal fee/emission data detected. Protocol operating in capital-accumulation or zero-fee state.")

        # Plotly Comparison Bar Chart
        fig_margin = go.Figure()
        fig_margin.add_trace(go.Bar(
            name="Gross Fees (USD)",
            x=["Protocol Economics"],
            y=[ann_fees],
            marker_color="#00ff87",
            text=[f"${ann_fees:,.0f}"],
            textposition='auto'
        ))
        fig_margin.add_trace(go.Bar(
            name="Emission Subsidies (USD)",
            x=["Protocol Economics"],
            y=[ann_inc],
            marker_color="#f87171",
            text=[f"${ann_inc:,.0f}"],
            textposition='auto'
        ))
        fig_margin.add_trace(go.Bar(
            name="Net Operating Income (USD)",
            x=["Protocol Economics"],
            y=[net_inc],
            marker_color="#00f2fe" if net_inc >= 0 else "#fb923c",
            text=[f"${net_inc:,.0f}"],
            textposition='auto'
        ))
        fig_margin.update_layout(
            barmode='group',
            height=260,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        apply_2027_theme(fig_margin, height=260)
        st.plotly_chart(fig_margin, use_container_width=True)

    # Tab 3: DAO Treasury Health & Liquid Solvency
    with tab_treasury:
        st.markdown("#### 🏦 DAO Treasury Health & Liquid Solvency")
        st.caption("Deconstructs DAO balance sheets into liquid non-native reserves (USDC/USDT/ETH/BTC) vs paper native governance tokens.")

        tot_treasury = float(treasury.get("total_treasury_usd", 0.0) if treasury else 0.0)
        liq_reserves = float(treasury.get("liquid_non_native_usd", 0.0) if treasury else 0.0)
        nat_treasury = float(treasury.get("native_tokens_usd", 0.0) if treasury else 0.0)
        liq_pct = float(treasury.get("liquid_ratio_pct", 0.0) if treasury else 0.0)
        m_burn = float(inst_metrics.get("monthly_burn_rate_usd", 0.0))
        runway_mo = float(inst_metrics.get("runway_months", 999.0))

        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            # Treasury Donut
            tot_t = liq_reserves + nat_treasury
            if tot_t > 0:
                t_labels = ["Liquid Reserves (Stables/ETH/BTC)", "Native Paper Tokens"]
                t_vals = [liq_reserves, nat_treasury]
                t_colors = ["#00ff87", "#475569"]
            else:
                t_labels = ["No Treasury Data"]
                t_vals = [1]
                t_colors = ["#334155"]

            fig_t = go.Figure(data=[go.Pie(
                labels=t_labels,
                values=t_vals,
                hole=.62,
                domain=dict(y=[0.20, 1.0]),
                marker=dict(colors=t_colors, line=dict(color='rgba(255,255,255,0.12)', width=1.5)),
                textinfo='percent',
                textposition='inside',
                insidetextfont=dict(size=11, family='JetBrains Mono, monospace', color='#ffffff'),
                hovertemplate="<b>%{label}</b><br>Value: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
            )])
            apply_2027_theme(fig_t, height=270)
            fig_t.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=270,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=10, family="Inter, sans-serif", color="#94a3b8")
                )
            )
            st.plotly_chart(fig_t, use_container_width=True)

        with col_t2:
            st.metric("Total Treasury Value", f"${tot_treasury:,.0f}")
            st.metric("Liquid Reserves Ratio", f"{liq_pct:.1f}% ({f'${liq_reserves:,.0f}'})")
            st.metric("Monthly Operating Burn", f"${m_burn:,.0f}")
            runway_str = f"{runway_mo:.1f} months" if runway_mo < 100 else "> 100 months (Infinite/Profitable)"
            st.metric("Estimated Liquid Runway", runway_str)

        if runway_mo < 12:
            st.error(f"🚨 **Fragile Runway Alarm**: Estimated liquid runway is only **{runway_mo:.1f} months**! If native token price declines, the DAO faces emergency spending cuts or forced secondary market dumping.")
        elif runway_mo < 24:
            st.warning(f"🟠 **Moderate Solvency**: Liquid runway is estimated at **{runway_mo:.1f} months**. Prudent balance sheet management required.")
        else:
            st.success(f"✅ **Institutional Solvency**: DAO maintains **{runway_str}** of liquid operating runway independent of native token price.")

        if profile and profile.get("treasury_details", {}).get("treasury_notes"):
            st.caption(f"**Treasury Notes:** {profile['treasury_details']['treasury_notes']}")

    # Tab 4: Dilution Price-Decay Simulator
    with tab_sim:
        st.markdown("#### 📉 Interactive Dilution Price-Decay & Break-Even Simulator")
        st.caption("Simulate token price trajectory under scheduled supply expansion assuming Flat Market Cap vs Growth/Contract Scenarios.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sim_horizon = st.slider("Projection Horizon (Months):", min_value=1, max_value=36, value=12, step=1, key="dilution_horizon")
        with col_s2:
            sim_mcap_pct = st.slider("Market Cap Sensitivity Scenario (%):", min_value=-50, max_value=300, value=0, step=10, key="dilution_mcap_sens", help="0% represents Flat Market Cap (pure dilution price decay). +50% represents 1.5x market cap expansion.")

        monthly_inf_pct = float(profile.get("unlock_schedule", {}).get("monthly_inflation_rate_pct", 0.0) if profile else 0.0)
        if monthly_inf_pct == 0.0 and profile:
            monthly_inf_pct = float(profile.get("incentives_and_emissions", {}).get("annual_inflation_rate_pct", 0.0)) / 12.0

        p0 = float(market_data.get("price_usd", 1.0) if market_data else 1.0)
        m0 = float(market_data.get("market_cap_usd", 1.0) if market_data else 1.0)
        s0 = float(market_data.get("circulating_supply", 1.0) if market_data else 1.0)

        months = list(range(sim_horizon + 1))
        supplies = []
        flat_prices = []
        scenario_prices = []
        m_rate = monthly_inf_pct / 100.0

        for m in months:
            s_m = s0 * ((1.0 + m_rate) ** m)
            supplies.append(s_m)
            p_flat = (m0 / s_m) if s_m > 0 else p0
            flat_prices.append(p_flat)
            m_scenario = m0 * (1.0 + (sim_mcap_pct / 100.0) * (m / sim_horizon))
            p_scen = (m_scenario / s_m) if s_m > 0 else p0
            scenario_prices.append(p_scen)

        p_flat_end = flat_prices[-1]
        p_scen_end = scenario_prices[-1]
        flat_decay_pct = ((p_flat_end - p0) / p0) * 100.0
        scen_change_pct = ((p_scen_end - p0) / p0) * 100.0
        supply_expansion_pct = ((supplies[-1] - s0) / s0) * 100.0
        be_mcap_growth_pct = ((supplies[-1] / s0) - 1.0) * 100.0

        sd1, sd2, sd3, sd4 = st.columns(4)
        with sd1:
            st.metric("Flat MCap Price (Month " + str(sim_horizon) + ")", f"${p_flat_end:.4f}" if p_flat_end < 1 else f"${p_flat_end:,.2f}", f"{flat_decay_pct:+.1f}% (Dilution Impact)", delta_color="normal" if flat_decay_pct >= 0 else "inverse")
        with sd2:
            st.metric("Scenario Price (Month " + str(sim_horizon) + ")", f"${p_scen_end:.4f}" if p_scen_end < 1 else f"${p_scen_end:,.2f}", f"{scen_change_pct:+.1f}% Scenario Delta", delta_color="normal" if scen_change_pct >= 0 else "inverse")
        with sd3:
            st.metric("Supply Expansion", f"{supply_expansion_pct:+.1f}%")
        with sd4:
            st.metric("Break-Even MCap Growth", f"{be_mcap_growth_pct:+.1f}%", help="Market cap growth required just to keep current price flat against scheduled emissions.")

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=months,
            y=[p0] * len(months),
            mode='lines',
            name=f"Current Baseline (${p0:.2f})",
            line=dict(color='rgba(255, 255, 255, 0.4)', dash='dash')
        ))
        fig_sim.add_trace(go.Scatter(
            x=months,
            y=flat_prices,
            mode='lines+markers',
            name="Flat MCap (Dilution Drag)",
            line=dict(color='#f87171', width=2, dash='dot')
        ))
        fig_sim.add_trace(go.Scatter(
            x=months,
            y=scenario_prices,
            mode='lines+markers',
            name=f"Scenario Price ({sim_mcap_pct:+d}% MCap)",
            line=dict(color='#00f2fe', width=3)
        ))
        apply_2027_theme(fig_sim, height=280)
        fig_sim.update_layout(
            title=dict(text=f"Implied Price Trajectory ({sim_horizon}-Month Model)", font=dict(family="Space Grotesk", size=13)),
            xaxis_title="Months Ahead",
            yaxis_title="Price ($ USD)",
            hovermode="x unified",
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    # Tab 5: Order Book Depth & Unlock Cliffs
    with tab_cliffs:
        st.markdown("#### ⏳ Order Book Depth & Cliff Slippage Fragility")
        st.caption("Quantifies liquidation fragility by comparing upcoming unlock cliff USD to live ±2% order book depth.")

        unsch = profile.get("unlock_schedule", {}) if profile else {}
        c_date = unsch.get("next_cliff_date", "N/A")
        c_usd = float(unsch.get("next_cliff_usd", 0.0))
        c_pct = float(unsch.get("next_cliff_pct_circulating", 0.0))
        depth_usd = float(depth.get("depth_2pct_usd", 0.0) if depth else 0.0)
        cliff_ratio = float(depth.get("cliff_to_depth_ratio", 0.0) if depth else 0.0)
        slip_level = depth.get("slippage_level", "Unknown") if depth else "Unknown"

        cd1, cd2, cd3, cd4 = st.columns(4)
        with cd1:
            st.metric("Next Major Cliff Date", str(c_date))
        with cd2:
            st.metric("Cliff USD Value", f"${c_usd:,.0f}" if c_usd > 0 else "None")
        with cd3:
            st.metric("Live ±2% Book Depth", f"${depth_usd:,.0f}")
        with cd4:
            st.metric("Cliff-to-Depth Ratio", f"{cliff_ratio:.1f}x Depth" if c_usd > 0 else "0.0x")

        if cliff_ratio >= 15.0:
            st.error(f"🚨 **Catastrophic Fragility Alert**: Upcoming cliff is **{cliff_ratio:.1f}x** the total ±2% order book depth ({slip_level})! Any liquidation by unlocked entities will cause severe slippage and price cascades.")
        elif cliff_ratio >= 5.0:
            st.warning(f"⚠️ **High Slippage Shock Risk**: Cliff represents **{cliff_ratio:.1f}x** available ±2% liquidity ({slip_level}).")
        elif c_usd == 0:
            st.success("✅ **Zero Cliff Fragility**: Zero upcoming founder or VC cliff unlocks. No structural liquidation overhang.")
        else:
            st.info(f"ℹ️ **Manageable Slippage Shock**: Cliff-to-depth ratio is **{cliff_ratio:.1f}x** ({slip_level}).")

        if unsch.get("cliff_notes"):
            st.caption(f"**Vesting & Cliff Notes:** {unsch['cliff_notes']}")

    # Tab 6: Whale Entities & Allocations
    with tab_whales:
        st.markdown("#### 🐋 Major Insider & Whale Entity Tracking")
        st.caption("Identifies structural insider concentrations, custody status, and potential dumping vectors.")

        entities = profile.get("major_entities", []) if profile else []
        if entities:
            e_records = []
            for e in entities:
                ent_name = e.get("entity", "Unknown")
                ent_type = e.get("type")
                if not ent_type:
                    low_name = ent_name.lower()
                    if any(w in low_name for w in ["vc", "fund", "investor", "capital", "venture"]):
                        ent_type = "Venture Syndicate"
                    elif any(w in low_name for w in ["team", "founder", "core", "cz", "contributor"]):
                        ent_type = "Founders & Insiders"
                    elif any(w in low_name for w in ["treasury", "reserve", "buffer", "foundation", "fund"]):
                        ent_type = "Treasury / Foundation"
                    elif any(w in low_name for w in ["public", "float", "market maker", "depositor"]):
                        ent_type = "Public / Free Float"
                    elif any(w in low_name for w in ["staked", "whale", "delegator", "trust", "etf"]):
                        ent_type = "Staking & Institutional"
                    else:
                        ent_type = "Strategic Entity"

                e_records.append({
                    "Entity / Cluster": ent_name,
                    "Cluster Type": ent_type,
                    "Share (%)": f"{e.get('percentage', 0.0):.1f}%",
                    "Custody / Lock Status": e.get("status") or e.get("custody", "Unspecified"),
                    "Dumping Risk Profile": e.get("dump_risk", "Moderate")
                })
            st.dataframe(pd.DataFrame(e_records), hide_index=True, use_container_width=True)
        else:
            st.caption("No specific entity tracking profiles found.")

        st.markdown("---")
        st.caption("**Genesis Token Allocation & Supply Breakdown**")
        if profile and profile.get("initial_allocation"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.caption("Genesis Token Allocation")
                alloc = profile.get("initial_allocation", {})
                alloc_map = [
                    ("Community / Airdrop", alloc.get("community_airdrop", 0), "#00f2fe"),
                    ("Treasury / Ecosystem", alloc.get("ecosystem_treasury", 0), "#3b82f6"),
                    ("Team / Founders", alloc.get("team_founders", 0), "#f43f5e"),
                    ("Investors / VCs", alloc.get("investors_vc", 0), "#a855f7"),
                    ("Public Sale", alloc.get("public_sale", 0), "#10b981")
                ]
                active_alloc = [item for item in alloc_map if item[1] > 0]
                if not active_alloc:
                    active_alloc = [("Standard Allocation", 100, "#3b82f6")]

                alloc_labels = [item[0] for item in active_alloc]
                alloc_vals = [item[1] for item in active_alloc]
                alloc_colors = [item[2] for item in active_alloc]

                fig_alloc = go.Figure(data=[go.Pie(
                    labels=alloc_labels,
                    values=alloc_vals,
                    hole=.58,
                    domain=dict(y=[0.20, 1.0]),
                    marker=dict(colors=alloc_colors, line=dict(color='rgba(255,255,255,0.12)', width=1.5)),
                    textinfo='percent',
                    textposition='inside',
                    insidetextfont=dict(size=11, family='JetBrains Mono, monospace', color='#ffffff'),
                    hovertemplate="<b>%{label}</b><br>Allocation: %{percent}<extra></extra>"
                )])
                apply_2027_theme(fig_alloc, height=270)
                fig_alloc.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=10, family="Inter, sans-serif", color="#94a3b8")
                    )
                )
                st.plotly_chart(fig_alloc, use_container_width=True)

            with col_a2:
                st.caption("Current Macro Supply Anatomy")
                circ = float(market_data.get("circulating_supply", 0.0) if market_data else 0.0)
                burned = float(market_data.get("burned_supply", 0.0) if market_data else 0.0)
                locked = float(market_data.get("locked_supply", 0.0) if market_data else 0.0)

                m_items = [("Circulating Float", circ, "#00ff87")]
                if burned > 0:
                    m_items.append(("Permanently Burned 🔥", burned, "#f43f5e"))
                if locked > 0:
                    m_items.append(("Locked Overhang 🔒", locked, "#f59e0b"))

                m_labels = [item[0] for item in m_items]
                m_vals = [item[1] for item in m_items]
                m_colors = [item[2] for item in m_items]

                fig_macro = go.Figure(data=[go.Pie(
                    labels=m_labels,
                    values=m_vals,
                    hole=.58,
                    domain=dict(y=[0.20, 1.0]),
                    marker=dict(colors=m_colors, line=dict(color='rgba(255,255,255,0.12)', width=1.5)),
                    textinfo='percent',
                    textposition='inside',
                    insidetextfont=dict(size=11, family='JetBrains Mono, monospace', color='#ffffff'),
                    hovertemplate="<b>%{label}</b><br>Tokens: %{value:,.0f}<br>Share: %{percent}<extra></extra>"
                )])
                apply_2027_theme(fig_macro, height=270)
                fig_macro.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=10, family="Inter, sans-serif", color="#94a3b8")
                    )
                )
                st.plotly_chart(fig_macro, use_container_width=True)

    # Tab 7: 5-Vector Radar Chart & Benchmark Rationale
    with tab_radar:
        st.markdown("#### 🕸️ 5-Vector Safety Radar & Metric Rationale")
        categories = [
            "Supply & Float",
            "Utility & Velocity",
            "Value Accrual",
            "Ecosystem & Depth",
            "Solvency & Cliffs"
        ]
        values = [scores["v1"], scores["v2"], scores["v3"], scores["v4"], scores["v5"]]
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        benchmark = [7.5, 7.5, 7.5, 7.5, 7.5, 7.5]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name=token_symbol,
            line=dict(color='#00f2fe', width=2.5),
            fillcolor='rgba(0, 242, 254, 0.22)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=benchmark,
            theta=categories_closed,
            name='Institutional Baseline (7.5)',
            line=dict(color='rgba(255, 255, 255, 0.35)', dash='dash')
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10, family="JetBrains Mono"), gridcolor="rgba(255,255,255,0.08)"),
                angularaxis=dict(tickfont=dict(size=10, color="#d1d5db", family="Space Grotesk"), gridcolor="rgba(255,255,255,0.08)")
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
            margin=dict(l=35, r=35, t=15, b=35),
            height=270,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        if market_data:
            breakdown_data = [
                {"Metric": "Float Ratio (MC / FDV)", "Value": f"{market_data['float_ratio']:.2f}", "Benchmark": ">= 0.80 (Healthy)", "Status": "✅ Low Risk" if market_data['float_ratio'] >= 0.8 else "⚠️ Dilution Overhang"},
                {"Metric": "Circulating Supply %", "Value": f"{market_data['circulating_pct']:.1f}%", "Benchmark": ">= 75% Unlocked", "Status": "✅ High Float" if market_data['circulating_pct'] >= 75 else "⚠️ Low Float"},
                {"Metric": "Locked Overhang Value", "Value": f"${market_data['locked_usd_value']:,.0f}", "Benchmark": "< $500M Overhang", "Status": "✅ Minimal" if market_data['locked_usd_value'] < 500_000_000 else "⚠️ Heavy Overhang"},
                {"Metric": "Turnover Velocity (24h Vol / MC)", "Value": f"{market_data['turnover_pct']:.2f}%", "Benchmark": ">= 4.0% Velocity", "Status": "✅ Active Utility" if market_data['turnover_pct'] >= 4 else "⚠️ Sluggish Velocity"},
                {"Metric": "ATH Retained (Price from ATH)", "Value": f"{market_data['ath_change_pct']:.1f}%", "Benchmark": "> -60.0% Retained", "Status": "✅ Value Retention" if market_data['ath_change_pct'] >= -60 else "⚠️ Value Erosion"},
                {"Metric": "Market Cap Dominance Rank", "Value": f"Rank #{market_data['market_cap_rank']}", "Benchmark": "Top 50 Dominance", "Status": "✅ Institutional Tier" if market_data['market_cap_rank'] <= 50 else "⚠️ Mid/Small Cap"}
            ]
            st.dataframe(pd.DataFrame(breakdown_data), hide_index=True, use_container_width=True)

    # Tab 8: Regulatory Matrix & Analyst Thesis
    with tab_thesis:
        st.markdown("#### ⚖️ Regulatory Matrix & Analyst Thesis")
        reg_info = profile.get("regulatory_classification", {}) if profile else {}

        cr1, cr2 = st.columns(2)
        with cr1:
            st.markdown(f"**Secondary Regulatory Classification:**\n`{reg_info.get('tag', 'General Crypto-Asset')}`")
            st.markdown(f"**US Howey Test Risk Level:** `{reg_info.get('howey_risk', 'Moderate')}`")
        with cr2:
            st.markdown(f"**EU MiCA Classification:** `{reg_info.get('mica_category', 'Crypto-Asset other than EMT/ART')}`")
            if reg_info.get("notes"):
                st.caption(f"**Regulatory Analysis:** {reg_info['notes']}")

        st.warning("""
        ⚖️ **The Cash Flow vs. Howey Paradox**: Tokens that distribute direct protocol revenue or execute programmatic buybacks face heightened US SEC / Howey Test securities classification risks as 'Investment Contracts'. Conversely, pure governance tokens with zero cash flows may minimize securities liability, but fail to provide intrinsic economic value capture for token holders.
        """)

        st.markdown("---")
        st.markdown("**Curated Institutional Analyst Thesis:**")
        if profile and profile.get("analyst_thesis"):
            th = profile["analyst_thesis"]
            st.markdown(f"**🟢 Bull Case Thesis:**\n{th.get('bull_case', 'N/A')}")
            st.markdown(f"**🔴 Bear Case / Structural Risks:**\n{th.get('bear_case', 'N/A')}")
            rf = th.get("red_flags", [])
            if rf:
                st.markdown("**⚠️ Flagged Red Flags:**")
                for r in rf:
                    st.error(f"🚩 {r}")
            else:
                st.success("✅ Zero structural red flags identified.")
        else:
            st.info("No curated analyst thesis available for this token. Use the Research Editor below to document your findings.")

# ---------------------------------------------------------
# Interactive Deep Tokenomics Research & Editor
# ---------------------------------------------------------
st.markdown("---")
with st.expander("✏️ Deep Tokenomics Research & Profile Editor (Custom Database)", expanded=False):
    st.caption("Inspect, customize, and save deep institutional tokenomics data (treasury details, emissions, staking yields, whale entities, and regulatory classification) directly into your local database (`data/token_profiles.json`).")
    
    with st.form("edit_profile_form"):
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            ed_symbol = st.text_input("Token Symbol:", value=profile.get("symbol", token_symbol) if profile else token_symbol)
            ed_name = st.text_input("Token Name:", value=profile.get("name", token_display_name) if profile else token_display_name)
            ed_category = st.text_input("Category:", value=profile.get("category", "DeFi / Layer 1") if profile else "DeFi")
            ed_slug = st.text_input("DeFiLlama Fee Slug (for live fees):", value=profile.get("defillama_slug", st.session_state.selected_coin_id) if profile else st.session_state.selected_coin_id)
            ed_treasury_slug = st.text_input("DeFiLlama Treasury Slug (for live treasury):", value=profile.get("treasury_details", {}).get("defillama_slug", "") if profile else "")
            
            accrual_types = [
                ("buyback_and_burn", "🔥 Active Buyback & Burn"),
                ("dual_burn_deflationary", "🔥 Dual Deflationary Burn"),
                ("fee_share_real_yield", "💎 Real Yield Fee Sharing"),
                ("gas_burn_deflationary", "⚡ Deflationary Fee Burn"),
                ("fee_switch_dormant", "⚠️ Dormant Fee Switch"),
                ("staking_emissions_only", "📉 Inflationary Staking Only"),
                ("pure_governance_no_cashflow", "⛔ Pure Governance (No Cash Flow)")
            ]
            current_accrual = profile.get("value_accrual_type", "buyback_and_burn") if profile else "buyback_and_burn"
            type_keys = [k for k, _ in accrual_types]
            idx_sel = type_keys.index(current_accrual) if current_accrual in type_keys else 0
            ed_accrual = st.selectbox("Value Accrual Architecture:", type_keys, index=idx_sel, format_func=lambda x: dict(accrual_types).get(x, x))
            
            ed_headline = st.text_input("Accrual Mechanism Summary:", value=profile.get("value_accrual_headline", "") if profile else "Protocol revenue model summary")
            
            # Staking inputs
            stk_prof = profile.get("staking_details", {}) if profile else {}
            ed_has_staking = st.checkbox("Active Staking Program?", value=stk_prof.get("has_staking", False))
            ed_nominal_apr = st.number_input("Nominal Staking APR (%):", value=float(stk_prof.get("nominal_staking_apr_pct") or stk_prof.get("annual_staking_apr_pct") or 0.0), step=0.1)
            ed_reward_asset = st.text_input("Staking Reward Asset:", value=stk_prof.get("reward_asset", "Native Token"))
            ed_stk_ratio = st.number_input("Staked Ratio (% of supply):", value=float(stk_prof.get("staking_ratio_pct", 0.0)), step=1.0)
            
        with col_ed2:
            ed_has_buyback = st.checkbox("Active Token Buybacks?", value=profile.get("buyback_details", {}).get("has_buyback", False) if profile else False)
            ed_buyback_mech = st.text_area("Buyback Description:", value=profile.get("buyback_details", {}).get("mechanism", "") if profile else "", height=68)
            
            ed_has_fee_switch = st.checkbox("Has Protocol Fee Switch?", value=profile.get("fee_switch_details", {}).get("has_fee_switch", False) if profile else False)
            ed_fee_switch_active = st.checkbox("Fee Switch Currently Active?", value=profile.get("fee_switch_details", {}).get("is_active", False) if profile else False)
            
            # Emissions & Incentives
            inc_prof = profile.get("incentives_and_emissions", {}) if profile else {}
            ed_ann_inc = st.number_input("Annual Token Incentives / Subsidies ($ USD):", value=float(inc_prof.get("annual_token_incentives_usd", 0.0)), step=1000000.0)
            ed_ann_inf = st.number_input("Annual Supply Inflation Rate (%):", value=float(inc_prof.get("annual_inflation_rate_pct", 0.0)), step=0.5)
            ed_is_mercenary = st.checkbox("Mercenary Capital Subsidized?", value=bool(inc_prof.get("is_mercenary_subsidized", False)))
            
            # Treasury details
            t_prof = profile.get("treasury_details", {}) if profile else {}
            col_tr1, col_tr2 = st.columns(2)
            with col_tr1:
                ed_liq_stables = st.number_input("Liquid Stables Reserves ($ USD):", value=float(t_prof.get("liquid_stables_usd", 0.0)), step=1000000.0)
                ed_monthly_burn = st.number_input("Monthly Operating Burn ($ USD):", value=float(t_prof.get("monthly_burn_rate_usd", 1500000.0)), step=100000.0)
            with col_tr2:
                ed_nat_treasury = st.number_input("Native Paper Treasury ($ USD):", value=float(t_prof.get("native_treasury_usd", 0.0)), step=1000000.0)

            # Cliffs
            col_cl1, col_cl2 = st.columns(2)
            with col_cl1:
                ed_cliff_date = st.text_input("Next Cliff Date:", value=profile.get("unlock_schedule", {}).get("next_cliff_date", "N/A") if profile else "N/A")
            with col_cl2:
                ed_cliff_usd = st.number_input("Cliff Amount ($ USD):", value=float(profile.get("unlock_schedule", {}).get("next_cliff_usd", 0.0) if profile else 0.0))
            
            ed_monthly_inf = st.number_input("Monthly Inflation Rate (%):", value=float(profile.get("unlock_schedule", {}).get("monthly_inflation_rate_pct", 0.0) if profile else 0.0), step=0.1)

        st.markdown("**Regulatory Classification & Institutional Thesis:**")
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            r_prof = profile.get("regulatory_classification", {}) if profile else {}
            ed_reg_tag = st.text_input("Regulatory Classification Tag:", value=r_prof.get("tag", "🟢 Commodity / Low Regulatory Risk"))
            ed_howey = st.selectbox("Howey Test Risk Level:", ["Low", "Moderate", "High / Securities Scrutiny"], index=0 if r_prof.get("howey_risk") == "Low" else (2 if "High" in str(r_prof.get("howey_risk")) else 1))
            ed_mica = st.text_input("EU MiCA Category:", value=r_prof.get("mica_category", "Crypto-Asset other than EMT/ART"))
            ed_reg_notes = st.text_area("Regulatory Analysis Notes:", value=r_prof.get("notes", ""), height=65)
        with col_reg2:
            ed_bull = st.text_area("Bull Case Thesis:", value=profile.get("analyst_thesis", {}).get("bull_case", "") if profile else "", height=65)
            ed_bear = st.text_area("Bear Case / Structural Risks:", value=profile.get("analyst_thesis", {}).get("bear_case", "") if profile else "", height=65)

        saved = st.form_submit_button("💾 Save Profile to Local Knowledge Base", use_container_width=True)
        if saved:
            mcap_val = market_data.get("market_cap_usd", 0.0) if market_data else 0.0
            new_prof = {
                "id": st.session_state.selected_coin_id,
                "symbol": ed_symbol.upper(),
                "name": ed_name,
                "category": ed_category,
                "defillama_slug": ed_slug,
                "value_accrual_type": ed_accrual,
                "value_accrual_headline": ed_headline,
                "revenue_sources": profile.get("revenue_sources", ["Protocol Services"]) if profile else ["Protocol Services"],
                "buyback_details": {
                    "has_buyback": ed_has_buyback,
                    "mechanism": ed_buyback_mech,
                    "frequency": "Configured by DAO / Foundation",
                    "annual_burn_runrate_est": profile.get("buyback_details", {}).get("annual_burn_runrate_est", "") if profile else ""
                },
                "fee_switch_details": {
                    "has_fee_switch": ed_has_fee_switch,
                    "is_active": ed_fee_switch_active,
                    "description": profile.get("fee_switch_details", {}).get("description", "") if profile else "",
                    "potential_annual_accrual": profile.get("fee_switch_details", {}).get("potential_annual_accrual", "") if profile else ""
                },
                "staking_details": {
                    "has_staking": ed_has_staking,
                    "is_real_yield": (ed_nominal_apr > ed_ann_inf) if ed_has_staking else False,
                    "staking_ratio_pct": ed_stk_ratio,
                    "reward_asset": ed_reward_asset,
                    "annual_staking_apr_pct": ed_nominal_apr,
                    "nominal_staking_apr_pct": ed_nominal_apr,
                    "real_staking_apr_pct": round(ed_nominal_apr - ed_ann_inf, 2)
                },
                "treasury_details": {
                    "defillama_slug": ed_treasury_slug,
                    "monthly_burn_rate_usd": ed_monthly_burn,
                    "liquid_stables_usd": ed_liq_stables,
                    "native_treasury_usd": ed_nat_treasury,
                    "treasury_notes": t_prof.get("treasury_notes", "")
                },
                "incentives_and_emissions": {
                    "annual_token_incentives_usd": ed_ann_inc,
                    "annual_inflation_rate_pct": ed_ann_inf,
                    "is_mercenary_subsidized": ed_is_mercenary
                },
                "major_entities": profile.get("major_entities", []) if profile else [],
                "regulatory_classification": {
                    "tag": ed_reg_tag,
                    "color": "#10b981" if ed_howey == "Low" else ("#f59e0b" if ed_howey == "Moderate" else "#ef4444"),
                    "howey_risk": ed_howey,
                    "mica_category": ed_mica,
                    "notes": ed_reg_notes
                },
                "initial_allocation": profile.get("initial_allocation", {"team_founders": 20.0, "investors_vc": 20.0, "community_airdrop": 10.0, "ecosystem_treasury": 40.0, "public_sale": 10.0}) if profile else {"team_founders": 20.0, "investors_vc": 20.0, "community_airdrop": 10.0, "ecosystem_treasury": 40.0, "public_sale": 10.0},
                "unlock_schedule": {
                    "vesting_status": profile.get("unlock_schedule", {}).get("vesting_status", "Active Vesting") if profile else "Active Vesting",
                    "next_cliff_date": ed_cliff_date,
                    "next_cliff_usd": ed_cliff_usd,
                    "next_cliff_pct_circulating": round((ed_cliff_usd / mcap_val * 100), 2) if mcap_val > 0 else 0.0,
                    "monthly_inflation_rate_pct": ed_monthly_inf,
                    "cliff_notes": profile.get("unlock_schedule", {}).get("cliff_notes", "") if profile else ""
                },
                "analyst_thesis": {
                    "bull_case": ed_bull,
                    "bear_case": ed_bear,
                    "red_flags": profile.get("analyst_thesis", {}).get("red_flags", []) if profile else []
                },
                "is_community_verified": True
            }
            token_db.save_profile(st.session_state.selected_coin_id, new_prof)
            st.success(f"Successfully saved research profile for {ed_symbol.upper()} to local database!")
            st.rerun()

# ---------------------------------------------------------
# Export & History Comparison
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📑 Report Export & Evaluation History")

col_save, col_dl1, col_dl2 = st.columns([1, 1, 1])

# Save to Session
with col_save:
    if st.button("💾 Save Token to Comparison Table", use_container_width=True):
        record = {
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Token": token_symbol,
            "Name": token_display_name,
            "Price ($)": round(market_data["price_usd"], 4) if market_data else 0.0,
            "Float Ratio": round(market_data["float_ratio"], 2) if market_data else 1.0,
            "Accrual Model": badge_text,
            "P/F Multiple": f"{financials['price_to_fees_ratio']}x" if (financials and financials.get("price_to_fees_ratio")) else "N/A",
            "Fee Yield": f"{financials['fee_yield_pct']:.1f}%" if (financials and financials.get("has_fees")) else "0.0%",
            "V1 (Supply)": scores["v1"],
            "V2 (Velocity)": scores["v2"],
            "V3 (Accrual)": scores["v3"],
            "V4 (Depth)": scores["v4"],
            "V5 (Solvency)": scores["v5"],
            "Safety Score": composite_score,
            "Grade": grade_info["grade"]
        }
        existing = [i for i, r in enumerate(st.session_state.token_history) if r["Token"] == token_symbol]
        if existing:
            st.session_state.token_history[existing[0]] = record
            st.success(f"Updated {token_symbol} in history!")
        else:
            st.session_state.token_history.append(record)
            st.success(f"Saved {token_symbol} to comparison list!")

# Markdown Report Download
with col_dl1:
    md_content = scoring.generate_markdown_report(
        token_name=token_display_name,
        scores=scores,
        weights=weights,
        composite_score=composite_score,
        grade_info=grade_info,
        market_data=market_data,
        vector_details=vector_details,
        profile=profile,
        financials=financials
    )
    st.download_button(
        label="📥 Download Markdown Report",
        data=md_content,
        file_name=f"{token_symbol}_tokenomics_report.md",
        mime="text/markdown",
        use_container_width=True
    )

# JSON Export Download
with col_dl2:
    export_payload = {
        "token": token_display_name,
        "symbol": token_symbol,
        "composite_score": composite_score,
        "grade": grade_info,
        "vectors": scores,
        "weights": weights,
        "market_data": market_data,
        "profile": profile,
        "financials": financials,
        "generated_at": datetime.now().isoformat()
    }
    st.download_button(
        label="📥 Download Raw JSON Data",
        data=json.dumps(export_payload, indent=2),
        file_name=f"{token_symbol}_tokenomics.json",
        mime="application/json",
        use_container_width=True
    )

# History Comparison Table
if st.session_state.token_history:
    st.markdown("### ⚖️ Multi-Token Comparison Table")
    history_df = pd.DataFrame(st.session_state.token_history)
    st.dataframe(
        history_df,
        hide_index=True,
        use_container_width=True
    )
    csv_data = history_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Comparison Table as CSV",
        data=csv_data,
        file_name="tokenomics_comparison_matrix.csv",
        mime="text/csv",
        use_container_width=True
    )
