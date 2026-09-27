"""
Tokenomics Scoring Engine and Automated Metric-Driven Evaluation Models (scoring.py)
Translates objective on-chain, market, protocol cash-flow, and tokenomics structure metrics
into institutional ratings and fundamental safety scores.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

VECTOR_METADATA = {
    "v1": {
        "id": "v1",
        "name": "Supply Dynamics & Float Ratio",
        "description": "Evaluates circulating float ratio (MC/FDV), non-circulating overhang, and supply ceiling finiteness.",
        "key_metrics": ["Float Ratio (Market Cap / FDV)", "Circulating Supply %", "Locked Overhang Value ($)", "Supply Hard Cap"],
        "key_questions": [
            "What % of total supply is already in circulation?",
            "Is the Float Ratio healthy (> 0.70) or is there massive future unlock pressure?",
            "Is there a mathematical hard cap on maximum supply?"
        ]
    },
    "v2": {
        "id": "v2",
        "name": "Utility & Market Demand Velocity",
        "description": "Evaluates transaction velocity, real platform fee burning, and genuine utility demand.",
        "key_metrics": ["Turnover Ratio (24h Vol / Market Cap)", "24h Volume ($)", "Protocol Fee Generation"],
        "key_questions": [
            "Are users actively transacting and burning the token for protocol services?",
            "Is the turnover ratio healthy (> 4%) showing organic velocity rather than illiquid speculation?",
            "Does token demand scale with real platform usage?"
        ]
    },
    "v3": {
        "id": "v3",
        "name": "Value Accrual & Cash Flow Safety",
        "description": "Evaluates direct economic cash flow capture: active buybacks & burns, real yield fee sharing, valuation multiples (P/F, P/S), and protocol cash flow.",
        "key_metrics": ["Value Capture Architecture", "Annualized Protocol Fees ($)", "Price-to-Fees (P/F Multiple)", "Fee Yield %", "ATH Cycle Resilience"],
        "key_questions": [
            "Does protocol revenue buy back and burn tokens, or distribute real dividends to holders?",
            "Is the token a pure zero-cash-flow governance meme with fee leakage to LPs/Founders?",
            "Is the Price-to-Fees multiple attractive (< 30x) providing fundamental downside support?"
        ]
    },
    "v4": {
        "id": "v4",
        "name": "Ecosystem Scale & Market Depth",
        "description": "Evaluates institutional liquidity, market capitalization tier, and exchange order-book depth.",
        "key_metrics": ["Market Cap Rank", "24h Liquidity Depth", "Institutional Presence"],
        "key_questions": [
            "Does the token hold deep, liquid market order books across Tier-1 exchanges?",
            "Where does it rank in global market dominance?",
            "Can institutional capital enter and exit without massive slippage?"
        ]
    },
    "v5": {
        "id": "v5",
        "name": "Dilution Solvency & Cliff Absorption",
        "description": "Evaluates the market's and protocol's ability to absorb upcoming token unlock cliffs without collapsing.",
        "key_metrics": ["Volume-to-Overhang Ratio", "Upcoming Cliff USD & % of Supply", "Annual Inflation vs Real Yield"],
        "key_questions": [
            "Can daily trading volume comfortably absorb token unlocks without tanking the price?",
            "Is there an imminent large VC/Team unlock cliff creating structural sell pressure?",
            "Is the token vulnerable to a low-float / high-FDV reflexivity trap?"
        ]
    }
}

DEFAULT_WEIGHTS = {
    "v1": 0.20,  # Dilution & supply dynamics
    "v2": 0.20,  # Velocity & utility
    "v3": 0.25,  # Value accrual & cash flow safety (highest weight)
    "v4": 0.15,  # Ecosystem scale & liquidity
    "v5": 0.20   # Solvency & cliff absorption
}


def calculate_grade(score: float) -> Dict[str, str]:
    """
    Map a composite score (0-10) to an institutional grade and verdict summary.
    """
    if score >= 9.0:
        return {
            "grade": "AAA (Fortress)",
            "short_grade": "AAA",
            "label": "Exceptional Tokenomics Fortress",
            "color": "#10b981",
            "verdict": "Tier-1 Cash Flow & Safety",
            "summary": "Outstanding tokenomics fundamentals. Proven revenue generation with active buybacks or real yield, mature circulating float, zero VC cliff overhang, and exceptional liquidity."
        }
    elif score >= 7.5:
        return {
            "grade": "AA (Strong)",
            "short_grade": "AA",
            "label": "Strong Fundamental Value",
            "color": "#3b82f6",
            "verdict": "Low to Moderate Risk",
            "summary": "Solid fundamentals with proven utility, manageable unlock schedules, healthy liquidity, and active or potential value accrual."
        }
    elif score >= 6.0:
        return {
            "grade": "BBB (Average)",
            "short_grade": "BBB",
            "label": "Average / Speculative Premium",
            "color": "#f59e0b",
            "verdict": "Moderate Risk / Mixed Accrual",
            "summary": "Acceptable float but limited direct cash-flow capture (e.g. dormant fee switch, or moderate unlock schedules). Requires ongoing network growth to justify valuation."
        }
    elif score >= 4.0:
        return {
            "grade": "BB (Elevated Risk)",
            "short_grade": "BB",
            "label": "Elevated Dilution Exposure",
            "color": "#f97316",
            "verdict": "Caution: Dilution / Low Accrual",
            "summary": "Significant structural headwinds. High FDV with ongoing token unlocks, or purely cosmetic governance rights with zero revenue accrual to holders."
        }
    else:
        return {
            "grade": "C / D (Severe Hazard)",
            "short_grade": "C",
            "label": "Severe Tokenomics Hazard",
            "color": "#ef4444",
            "verdict": "High Risk of Dilution Cascade",
            "summary": "Predatory tokenomics structure. Massive locked overhang (float < 0.20), heavy upcoming cliff unlocks, zero protocol revenue, and severe inflationary emissions."
        }


def compute_metric_driven_tokenomics(
    market_data: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    financials: Optional[Dict[str, Any]] = None,
    treasury: Optional[Dict[str, Any]] = None,
    depth: Optional[Dict[str, Any]] = None,
    inst_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute 100% automated, objective scores for all 5 vectors based strictly
    on real-world market metrics, protocol cash flows, buyback mechanics, and unlock cliffs.
    """
    float_ratio = float(market_data.get("float_ratio", 1.0))
    circulating_pct = float(market_data.get("circulating_pct", 100.0))
    locked_usd = float(market_data.get("locked_usd_value", 0.0))
    volume_24h = float(market_data.get("volume_24h_usd", 0.0))
    market_cap = float(market_data.get("market_cap_usd", 0.0))
    ath_drop = float(market_data.get("ath_change_pct", 0.0))
    rank = int(market_data.get("market_cap_rank") or 999)
    turnover = float(market_data.get("turnover_pct", 0.0))
    categories = [c.lower() for c in market_data.get("categories", [])]
    genesis_date = market_data.get("genesis_date")

    # -------------------------------------------------------------
    # Vector 1: Supply Dynamics & Dilution Overhang (Float & Ceilings)
    # -------------------------------------------------------------
    if float_ratio >= 0.95:
        v1_base = 9.8
    elif float_ratio >= 0.80:
        v1_base = 8.5 + (float_ratio - 0.80) * 8.6
    elif float_ratio >= 0.50:
        v1_base = 6.5 + (float_ratio - 0.50) * 6.6
    elif float_ratio >= 0.25:
        v1_base = 4.0 + (float_ratio - 0.25) * 10.0
    elif float_ratio >= 0.10:
        v1_base = 2.0 + (float_ratio - 0.10) * 13.3
    else:
        v1_base = max(1.0, float_ratio * 20.0)

    # Supply cap and overhang adjustments
    if market_data.get("max_supply") and market_data.get("max_supply") == market_data.get("total_supply"):
        v1_base += 0.3  # Finite mathematical hard cap
    if circulating_pct >= 90.0:
        v1_base += 0.2
    if locked_usd > 1_500_000_000 and float_ratio < 0.50:
        v1_base -= 0.6  # Heavy dollar overhang penalty

    # Inflation from profile
    if profile and profile.get("unlock_schedule"):
        m_inf = profile["unlock_schedule"].get("monthly_inflation_rate_pct", 0.0)
        if m_inf < 0:
            v1_base += 0.4  # Net deflationary burning!
        elif m_inf > 2.0:
            v1_base -= 0.6  # High ongoing inflation (>24%/yr)

    v1_score = round(max(1.0, min(10.0, v1_base)), 1)
    v1_headline = f"Float Ratio: {float_ratio:.2f} ({circulating_pct:.1f}% Unlocked)"
    v1_evidence = (
        f"{'Near zero dilution overhang. Supply is mature and non-inflationary.' if float_ratio >= 0.85 else ('Moderate unlock overhang.' if float_ratio >= 0.50 else f'High dilution overhang (${locked_usd:,.0f} locked).')}"
    )

    # -------------------------------------------------------------
    # Vector 2: Utility & Demand Velocity (Turnover & Protocol Fees)
    # -------------------------------------------------------------
    if turnover >= 20.0:
        v2_base = 9.5
    elif turnover >= 10.0:
        v2_base = 8.5 + (turnover - 10.0) * 0.1
    elif turnover >= 4.0:
        v2_base = 7.0 + (turnover - 4.0) * 0.25
    elif turnover >= 1.5:
        v2_base = 5.0 + (turnover - 1.5) * 0.8
    else:
        v2_base = max(1.5, turnover * 3.3)

    # Category utility adjustments
    is_l1 = any("layer 1" in c or "smart contract" in c or "infrastructure" in c for c in categories) or (profile and "layer 1" in profile.get("category", "").lower())
    is_defi = any("defi" in c or "decentralized finance" in c or "dex" in c for c in categories) or (profile and "defi" in profile.get("category", "").lower())

    if is_l1:
        v2_base += 0.5
    elif is_defi:
        v2_base += 0.3

    # Protocol fee velocity bonus
    ann_fees = financials.get("annualized_fees_usd", 0.0) if financials else 0.0
    if ann_fees >= 100_000_000:
        v2_base += 0.8  # Massive real economic velocity ($100M+ fees)
    elif ann_fees >= 15_000_000:
        v2_base += 0.4

    v2_score = round(max(1.0, min(10.0, v2_base)), 1)
    fee_str = f" | Ann. Fees: ${ann_fees:,.0f}" if ann_fees > 0 else ""
    v2_headline = f"Turnover: {turnover:.2f}% (Vol: ${volume_24h:,.0f}){fee_str}"
    v2_evidence = (
        f"{'Tier-1 network utility with high transaction velocity.' if (is_l1 or is_defi) and turnover >= 4 else ('Active organic trading velocity.' if turnover >= 4 else 'Low trading velocity; speculative turnover.')}"
    )

    # -------------------------------------------------------------
    # Vector 3: Value Accrual & Cash Flow Safety (Buybacks & Revenue)
    # -------------------------------------------------------------
    accrual_type = profile.get("value_accrual_type") if profile else "unknown"
    
    # 1. Structural Economic Capture Base Score
    if accrual_type == "buyback_and_burn":
        v3_structural = 9.0  # Open-market buybacks actively reduce supply
        accrual_label = "🔥 Active Buyback & Burn"
    elif accrual_type in ["dual_burn_deflationary", "dual_burn"]:
        v3_structural = 9.2  # Dual engine: quarterly auto-burn + real-time BEP-95 gas burn
        accrual_label = "🔥 Dual Deflationary Burn"
    elif accrual_type == "fee_share_real_yield":
        v3_structural = 9.0  # Real yield in ETH/USDC/native revenue
        accrual_label = "💎 Real Yield Fee Sharing"
    elif accrual_type == "gas_burn_deflationary":
        v3_structural = 8.4  # Algorithmic fee burn
        accrual_label = "⚡ Deflationary Fee Burn"
    elif accrual_type == "fee_switch_dormant":
        v3_structural = 6.0  # High protocol revenue, but dormant token claim
        accrual_label = "⚠️ Dormant Fee Switch"
    elif accrual_type == "staking_emissions_only":
        v3_structural = 4.0  # Inflationary staking (no protocol cash flow)
        accrual_label = "📉 Inflationary Staking Only"
    elif accrual_type == "pure_governance_no_cashflow":
        v3_structural = 3.2  # Zero economic cash flow
        accrual_label = "⛔ Pure Governance (No Cash Flow)"
    else:
        v3_structural = 6.0 if is_l1 or is_defi else 4.5
        accrual_label = "General Utility"

    # 2. Valuation Multiples & Protocol Cash Flow (DeFiLlama)
    if financials and financials.get("has_fees"):
        pf = financials.get("price_to_fees_ratio")
        fee_yield = financials.get("fee_yield_pct", 0.0)
        
        if pf and pf <= 15.0:
            v3_structural += 1.0  # Deep value (<15x P/F)
        elif pf and pf <= 35.0:
            v3_structural += 0.5  # Attractive institutional valuation
        elif pf and pf > 120.0:
            v3_structural -= 0.8  # Speculative growth premium (>120x P/F)

        if fee_yield >= 15.0:
            v3_structural += 0.6
        elif fee_yield >= 5.0:
            v3_structural += 0.3
    elif accrual_type in ["staking_emissions_only", "pure_governance_no_cashflow"]:
        v3_structural -= 0.8  # Confirmed zero protocol revenue capture

    # Net Protocol Margin & Mercenary Emissions adjustment
    if inst_metrics:
        net_inc = inst_metrics.get("net_protocol_income_usd", 0.0)
        ann_f = inst_metrics.get("annualized_fees_usd", 0.0)
        ann_inc = inst_metrics.get("annual_incentives_usd", 0.0)
        if net_inc >= 25_000_000:
            v3_structural += 0.8  # Profitable economic flywheel
        elif ann_f > 0 and net_inc < -15_000_000:
            v3_structural -= 1.2  # Heavy mercenary capital bleeding!
        elif ann_f == 0 and ann_inc > 20_000_000:
            v3_structural -= 1.0  # Dilution with zero fees

        real_apr = inst_metrics.get("real_staking_apr_pct", 0.0)
        if real_apr < -2.0:
            v3_structural -= 0.6  # Dilutionary staking trap
        elif real_apr >= 4.0:
            v3_structural += 0.4  # Real positive cash yield

    # 3. Cycle Price Resilience (ATH Drawdown test - 35% weight)
    if ath_drop >= -30.0:
        ath_s = 9.6
    elif ath_drop >= -55.0:
        ath_s = 8.0 + (ath_drop + 55.0) * 0.064
    elif ath_drop >= -75.0:
        ath_s = 6.0 + (ath_drop + 75.0) * 0.10
    elif ath_drop >= -90.0:
        ath_s = 3.5 + (ath_drop + 90.0) * 0.16
    else:
        ath_s = max(1.0, 1.0 + (ath_drop + 100.0) * 0.25)

    # Blended Vector 3: 65% structural accrual & cash flow safety + 35% cycle price resilience
    v3_score = round(max(1.0, min(10.0, v3_structural * 0.65 + ath_s * 0.35)), 1)
    
    pf_disp = f" | P/F: {financials['price_to_fees_ratio']}x" if (financials and financials.get("price_to_fees_ratio")) else ""
    v3_headline = f"{accrual_label}{pf_disp} | ATH: {ath_drop:+.1f}%"
    v3_evidence = (
        profile.get("value_accrual_headline") if (profile and profile.get("value_accrual_headline"))
        else ("Direct protocol cash-flow capture active." if v3_structural >= 7.5 else "Limited or dormant token value accrual.")
    )

    # -------------------------------------------------------------
    # Vector 4: Ecosystem Scale & Market Depth (Rank & Liquidity)
    # -------------------------------------------------------------
    if rank <= 3:
        rank_s = 10.0
    elif rank <= 10:
        rank_s = 9.3
    elif rank <= 25:
        rank_s = 8.5
    elif rank <= 50:
        rank_s = 7.6
    elif rank <= 100:
        rank_s = 6.6
    elif rank <= 250:
        rank_s = 5.2
    else:
        rank_s = max(2.0, 5.0 - (rank - 250) * 0.005)

    if volume_24h >= 1_000_000_000:
        vol_s = 10.0
    elif volume_24h >= 250_000_000:
        vol_s = 8.8
    elif volume_24h >= 50_000_000:
        vol_s = 7.5
    elif volume_24h >= 10_000_000:
        vol_s = 6.0
    elif volume_24h >= 2_000_000:
        vol_s = 4.5
    else:
        vol_s = 2.5

    v4_score = round(max(1.0, min(10.0, rank_s * 0.6 + vol_s * 0.4)), 1)
    v4_headline = f"Market Rank #{rank} | 24h Vol: ${volume_24h:,.0f}"
    v4_evidence = (
        f"{'Global blue-chip scale with institutional order-book depth.' if rank <= 10 else ('Strong Tier-1 market presence.' if rank <= 50 else 'Mid-cap / emerging liquidity depth.')}"
    )

    # -------------------------------------------------------------
    # Vector 5: Dilution Solvency & Cliff Absorption (Overhang & Cliffs)
    # -------------------------------------------------------------
    vol_overhang_ratio = market_data.get("vol_overhang_ratio", 999.0)

    if float_ratio >= 0.95 or locked_usd == 0:
        v5_base = 9.8
        abs_summary = "Zero locked overhang. Fully immune to unlock dump cascades."
    elif vol_overhang_ratio >= 0.20:
        v5_base = 8.5
        abs_summary = f"High daily volume (${volume_24h:,.0f}) easily absorbs unlock emissions."
    elif vol_overhang_ratio >= 0.05:
        v5_base = 7.0 + (vol_overhang_ratio - 0.05) * 10.0
        abs_summary = "Manageable unlock overhang relative to trading liquidity."
    elif vol_overhang_ratio >= 0.01:
        v5_base = 4.5 + (vol_overhang_ratio - 0.01) * 62.5
        abs_summary = "Vulnerable: Locked overhang is 20x-100x larger than daily volume."
    else:
        v5_base = max(1.5, vol_overhang_ratio * 300.0)
        abs_summary = "Severe danger: Locked overhang dwarfs daily volume by >100x."

    # Upcoming cliff shock penalty
    if profile and profile.get("unlock_schedule"):
        cliff_pct = profile["unlock_schedule"].get("next_cliff_pct_circulating", 0.0)
        cliff_usd = profile["unlock_schedule"].get("next_cliff_usd", 0.0)
        if cliff_pct >= 10.0 or (volume_24h > 0 and cliff_usd > volume_24h * 4):
            v5_base -= 1.5  # Severe cliff shock imminent!
            abs_summary = f"⚠️ High Cliff Shock: Upcoming unlock (${cliff_usd:,.0f}) is {cliff_pct:.1f}% of circulating supply!"
        elif cliff_pct >= 4.0:
            v5_base -= 0.7

    # Slippage Fragility vs 2% Depth
    if depth:
        c_depth_ratio = float(depth.get("cliff_to_depth_ratio", 0.0))
        if c_depth_ratio >= 15.0:
            v5_base -= 1.2
            abs_summary += f" | Extreme Slippage: Cliff is {c_depth_ratio:.1f}x 2% order book depth!"
        elif c_depth_ratio >= 5.0:
            v5_base -= 0.6
            abs_summary += f" | High Slippage: Cliff is {c_depth_ratio:.1f}x 2% depth."

    # Liquid Treasury Runway Solvency
    if inst_metrics:
        r_months = float(inst_metrics.get("runway_months", 999.0))
        burn_r = float(inst_metrics.get("monthly_burn_rate_usd", 0.0))
        if burn_r > 0 and r_months < 6.0:
            v5_base -= 1.5
            abs_summary += f" | 🚨 Critical Runway: Only {r_months:.1f} months of liquid stablecoins remaining!"
        elif burn_r > 0 and r_months < 12.0:
            v5_base -= 0.6
        elif r_months >= 36.0:
            v5_base += 0.3

    if float_ratio < 0.25:
        v5_base -= 0.8  # Structural low-float penalty

    v5_score = round(max(1.0, min(10.0, v5_base)), 1)
    v5_headline = f"Absorption Ratio: {vol_overhang_ratio:.2f}x Daily Vol vs Overhang"
    v5_evidence = abs_summary

    vectors = {
        "v1": {
            "name": VECTOR_METADATA["v1"]["name"],
            "score": v1_score,
            "headline": v1_headline,
            "evidence": v1_evidence,
            "metric_key": f"Float: {float_ratio:.2f} | Unlocked: {circulating_pct:.1f}%"
        },
        "v2": {
            "name": VECTOR_METADATA["v2"]["name"],
            "score": v2_score,
            "headline": v2_headline,
            "evidence": v2_evidence,
            "metric_key": f"Turnover: {turnover:.2f}% | Vol: ${volume_24h:,.0f}"
        },
        "v3": {
            "name": VECTOR_METADATA["v3"]["name"],
            "score": v3_score,
            "headline": v3_headline,
            "evidence": v3_evidence,
            "metric_key": f"Accrual: {accrual_label}"
        },
        "v4": {
            "name": VECTOR_METADATA["v4"]["name"],
            "score": v4_score,
            "headline": v4_headline,
            "evidence": v4_evidence,
            "metric_key": f"Rank #{rank} | Liquidity: ${volume_24h:,.0f}"
        },
        "v5": {
            "name": VECTOR_METADATA["v5"]["name"],
            "score": v5_score,
            "headline": v5_headline,
            "evidence": v5_evidence,
            "metric_key": f"Vol/Overhang: {vol_overhang_ratio:.2f}x | Overhang: ${locked_usd:,.0f}"
        }
    }

    # Institutional Warning Flags & Red Badges
    warning_badges = []
    if inst_metrics:
        r_months = float(inst_metrics.get("runway_months", 999.0))
        burn_r = float(inst_metrics.get("monthly_burn_rate_usd", 0.0))
        if burn_r > 0 and r_months < 6.0:
            warning_badges.append({
                "text": "🚨 Fragile Runway (<6 mo Liquid)",
                "style": "badge-red",
                "tooltip": "DAO liquid non-native reserves are insufficient to cover 6 months of operational burn without selling native tokens."
            })
        if inst_metrics.get("is_mercenary_subsidized"):
            warning_badges.append({
                "text": "⚠️ Mercenary Capital: Negative Net Income",
                "style": "badge-orange",
                "tooltip": "Token emissions and farming subsidies exceed gross protocol revenue, creating net dilutionary drag."
            })
        if float(inst_metrics.get("real_staking_apr_pct", 0.0)) < -1.5:
            warning_badges.append({
                "text": "📉 Dilutionary Yield Trap (Negative Real APR)",
                "style": "badge-orange",
                "tooltip": "Network token inflation is higher than nominal staking APY; stakers are losing purchasing power."
            })
        if float(inst_metrics.get("insider_pct", 0.0)) >= 50.0:
            warning_badges.append({
                "text": f"🐋 Whale Cartel: Insiders Control {inst_metrics['insider_pct']:.0f}%",
                "style": "badge-orange",
                "tooltip": "Over 50% of supply is held by concentrated insider, team, or venture fund clusters."
            })

    if depth and float(depth.get("cliff_to_depth_ratio", 0.0)) >= 8.0:
        warning_badges.append({
            "text": f"💥 High Slippage Fragility ({depth['cliff_to_depth_ratio']:.1f}x 2% Depth)",
            "style": "badge-red",
            "tooltip": "Upcoming unlock dwarfs the entire exchange order-book depth, creating extreme flash-crash risk."
        })

    if profile and profile.get("regulatory_classification", {}).get("color") == "red":
        warning_badges.append({
            "text": "🏛️ High Securities Scrutiny / Dividend Token",
            "style": "badge-red",
            "tooltip": "Direct revenue sharing exposes this protocol to US SEC Howey investment contract enforcement."
        })

    raw_scores = {k: v["score"] for k, v in vectors.items()}
    composite = compute_weighted_score(raw_scores, DEFAULT_WEIGHTS)
    grade = calculate_grade(composite)

    return {
        "scores": raw_scores,
        "vector_details": vectors,
        "composite_score": composite,
        "grade_info": grade,
        "weights": DEFAULT_WEIGHTS,
        "accrual_label": accrual_label,
        "value_accrual_type": accrual_type,
        "warning_badges": warning_badges,
        "inst_metrics": inst_metrics or {},
        "depth": depth or {},
        "treasury": treasury or {}
    }


def compute_weighted_score(
    scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Compute normalized weighted score from 0.0 to 10.0."""
    w = weights if weights else DEFAULT_WEIGHTS
    total_weight = sum(w.get(k, 0.0) for k in ["v1", "v2", "v3", "v4", "v5"])
    if total_weight <= 0:
        total_weight = 1.0

    weighted_sum = sum(
        scores.get(k, 5.0) * (w.get(k, 0.0) / total_weight)
        for k in ["v1", "v2", "v3", "v4", "v5"]
    )
    return round(max(0.0, min(10.0, weighted_sum)), 2)


def generate_markdown_report(
    token_name: str,
    scores: Dict[str, float],
    weights: Dict[str, float],
    composite_score: float,
    grade_info: Dict[str, str],
    market_data: Optional[Dict[str, Any]] = None,
    vector_details: Optional[Dict[str, Any]] = None,
    profile: Optional[Dict[str, Any]] = None,
    financials: Optional[Dict[str, Any]] = None
) -> str:
    """Generate an institutional tokenomics research report with deep financial metrics."""
    lines = [
        f"# Institutional Tokenomics Rating Report: {token_name.upper()}",
        "",
        f"**Safety Score:** `{composite_score:.2f} / 10.0` — **Grade:** **{grade_info['grade']}**",
        f"**Verdict:** *{grade_info['verdict']}*",
        f"> *{grade_info['summary']}*",
        "",
        "---",
        ""
    ]

    if financials and financials.get("has_fees"):
        lines.extend([
            "## Protocol Financials & Valuation Multiples (DeFiLlama)",
            f"- **24h Protocol Fees:** `${financials.get('fees_24h_usd', 0):,.0f}`",
            f"- **Annualized Protocol Fees:** `${financials.get('annualized_fees_usd', 0):,.0f}`",
            f"- **Price-to-Fees (P/F Multiple):** `{financials.get('price_to_fees_ratio', 'N/A')}x`",
            f"- **Annualized Fee Yield:** `{financials.get('fee_yield_pct', 0.0):.2f}%`",
            "",
            "---",
            ""
        ])

    if profile:
        lines.extend([
            "## Value Accrual & Tokenomics Structure",
            f"- **Value Accrual Architecture:** `{profile.get('value_accrual_type', 'N/A')}`",
            f"- **Accrual Summary:** {profile.get('value_accrual_headline', 'N/A')}",
            f"- **Active Buybacks:** {'Yes' if profile.get('buyback_details', {}).get('has_buyback') else 'No'}",
            f"- **Buyback Description:** {profile.get('buyback_details', {}).get('mechanism', 'None')}",
            f"- **Fee Switch Status:** {'Active' if profile.get('fee_switch_details', {}).get('is_active') else 'Inactive / Dormant'}",
            f"- **Vesting & Cliffs:** {profile.get('unlock_schedule', {}).get('vesting_status', 'N/A')}",
            "",
            "---",
            ""
        ])

    if market_data:
        lines.extend([
            "## Quantitative Token Fundamentals",
            f"- **Price (USD):** `${market_data.get('price_usd', 0):,.4f}`",
            f"- **Market Cap:** `${market_data.get('market_cap_usd', 0):,.0f}` (Rank #{market_data.get('market_cap_rank', 'N/A')})",
            f"- **Fully Diluted Valuation (FDV):** `${market_data.get('fdv_usd', 0):,.0f}`",
            f"- **Float Ratio (MC / FDV):** `{market_data.get('float_ratio', 0):.2f}` ({market_data.get('dilution_risk_level', 'N/A')})",
            f"- **Circulating Supply:** `{market_data.get('circulating_supply', 0):,.0f}` ({market_data.get('circulating_pct', 0):.1f}% unlocked)",
            f"- **Locked Overhang Supply Value:** `${market_data.get('locked_usd_value', 0):,.0f} USD`",
            f"- **24h Trading Turnover:** `{market_data.get('turnover_pct', 0):.2f}%` (24h Vol: `${market_data.get('volume_24h_usd', 0):,.0f}`)",
            f"- **ATH Drawdown:** `{market_data.get('ath_change_pct', 0):+.2f}%`",
            "",
            "---",
            ""
        ])

    lines.extend([
        "## Vector Scorecard & Metric Evidence",
        "| Vector | Score | Weight | Primary Quantitative Driver | Evidence & Assessment |",
        "| :--- | :---: | :---: | :--- | :--- |"
    ])

    for key, meta in VECTOR_METADATA.items():
        score = scores.get(key, 5.0)
        weight_pct = f"{weights.get(key, 0.2) * 100:.0f}%"
        detail = (vector_details or {}).get(key, {})
        headline = detail.get("headline", meta["name"])
        evidence = detail.get("evidence", "Standard metric evaluation")
        lines.append(f"| **{meta['name']}** | `{score:.1f}/10.0` | `{weight_pct}` | {headline} | {evidence} |")

    lines.extend([
        "",
        "## Strategic Conclusion",
        f"- **Cash Flow Safety**: {'Exceptional cash flow capture with active buybacks or real yield.' if (profile and profile.get('value_accrual_type') in ['buyback_and_burn', 'fee_share_real_yield']) else 'Limited direct cash flow capture; token is speculative or governance-only.'}",
        f"- **Dilution Exposure**: {'Minimal dilution risk.' if (market_data and market_data.get('float_ratio', 1.0) >= 0.8) else 'Heavy supply unlock overhang; monitor token unlock schedules closely.'}",
        "- **Assessment Source**: Quantitative Tokenomics & Value Accrual Engine."
    ])

    return "\n".join(lines)
