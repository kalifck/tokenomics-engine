"""
Crypto Tokenomics Analyzer & Rating Tool (CLI Edition)
Institutional Metric-Driven Tokenomics Rating System & Red Flag Engine
"""

import sys
import argparse
import api_service
import scoring
import token_db


def get_float_input(prompt, min_val=0.0, max_val=10.0, default=None):
    if default is not None:
        prompt_str = f"{prompt} [{default:.1f}]: "
    else:
        prompt_str = prompt

    while True:
        try:
            val_str = input(prompt_str).strip()
            if not val_str and default is not None:
                return float(default)
            val = float(val_str)
            if min_val <= val <= max_val:
                return val
            print(f"Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def _clean(txt):
    if not txt:
        return ""
    return str(txt).encode("ascii", "ignore").decode("ascii").strip()


def display_report(token_name, symbol, scores, avg_score, grade_info, market_data=None, vector_details=None, profile=None, financials=None, treasury=None, depth=None, inst_metrics=None, warning_badges=None):
    print("\n" + "=" * 70)
    print(f" INSTITUTIONAL TOKENOMICS REPORT CARD: {token_name.upper()} ({symbol.upper()})")
    print("=" * 70)

    if profile:
        acc_type = _clean(profile.get('value_accrual_type', 'N/A'))
        reg_tag = _clean(profile.get('regulatory_classification', {}).get('tag', 'N/A'))
        print(f"| Value Accrual Model:    {acc_type:<38} |")
        print(f"| Regulatory Tag:         {reg_tag:<38} |")
        has_bb = profile.get("buyback_details", {}).get("has_buyback", False)
        print(f"| Active Buybacks:        {'Yes (Protocol Funded)' if has_bb else 'No Buyback Program':<38} |")
        
        if financials and financials.get("has_fees"):
            print(f"| 24h Protocol Fees:      ${financials.get('fees_24h_usd', 0):>15,.0f}              |")
            print(f"| Annualized Fee Runrate: ${financials.get('annualized_fees_usd', 0):>15,.0f}              |")
            pf_val = financials.get('price_to_fees_ratio')
            print(f"| Price-to-Fees (P/F):     {f'{pf_val}x' if pf_val else 'N/A':>15}              |")
        
        if inst_metrics:
            net_inc = inst_metrics.get("net_protocol_income_usd", 0.0)
            net_marg = inst_metrics.get("net_margin_pct", 0.0)
            print(f"| Net Operating Income:   ${net_inc:>15,.0f} ({net_marg:+.1f}%)        |")
            real_apr = inst_metrics.get("real_staking_apr_pct", 0.0)
            nom_apr = inst_metrics.get("nominal_staking_apr_pct", 0.0)
            print(f"| Real Staking APR:        {f'{real_apr:+.2f}%' if nom_apr > 0 else 'N/A':>15}              |")
            runway = inst_metrics.get("runway_months", 999.0)
            print(f"| Liquid Solvency Runway:  {f'{runway:.1f} months' if runway < 100 else '>100 months':>15}              |")
        print("-" * 70)

    if market_data:
        print(f"| Price (USD):            ${market_data.get('price_usd', 0):>15,.4f}              |")
        print(f"| Market Cap:             ${market_data.get('market_cap_usd', 0):>15,.0f} (Rank #{market_data.get('market_cap_rank', 'N/A')})  |")
        print(f"| Fully Diluted (FDV):    ${market_data.get('fdv_usd', 0):>15,.0f}              |")
        print(f"| Float Ratio (MC/FDV):    {market_data.get('float_ratio', 0):>15.2f}              |")
        print(f"| Circulating Supply:      {market_data.get('circulating_pct', 0):>14.1f}%              |")
        b_sup = market_data.get('burned_supply', 0.0)
        if b_sup > 0:
            print(f"| Permanently Burned:      {market_data.get('burned_pct', 0):>14.1f}% ({b_sup:,.0f})     |")
        print(f"| Locked Overhang ($):    ${market_data.get('locked_usd_value', 0):>15,.0f}              |")
        print(f"| Turnover Velocity:       {market_data.get('turnover_pct', 0):>14.2f}%              |")
        print(f"| ATH Drawdown:            {market_data.get('ath_change_pct', 0):>14.1f}%              |")
        if depth:
            c_ratio = depth.get("cliff_to_depth_ratio", 0.0)
            print(f"| Cliff / 2% Depth Ratio:  {f'{c_ratio:.1f}x' if c_ratio > 0 else '0.0x':>15}              |")
        print("-" * 70)

    if warning_badges:
        print("INSTITUTIONAL RISK ALERTS / WARNING FLAGS:")
        for b in warning_badges:
            b_txt = _clean(b.get('text', ''))
            print(f"  [!] {b_txt}")
        print("-" * 70)

    print("5-VECTOR SCORECARD & METRIC DRIVERS:")
    for vid, meta in scoring.VECTOR_METADATA.items():
        sc = scores.get(vid, 5.0)
        vinfo = (vector_details or {}).get(vid, {})
        driver = _clean(vinfo.get("headline", meta["name"]))
        print(f"  [{sc:4.1f}/10.0] {_clean(meta['name'])}")
        print(f"           Driver: {driver}")

    print("-" * 70)
    print(f" FINAL SCORE : {avg_score:.2f} / 10.0")
    print(f" GRADE       : {_clean(grade_info['grade'])}")
    print(f" VERDICT     : {_clean(grade_info['verdict'])}")
    print(f" ASSESSMENT  : {_clean(grade_info['summary'])}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Crypto Tokenomics Analyzer & Rating Engine (CLI)")
    parser.add_argument("--coin", "-c", help="CoinGecko ID or ticker (e.g. bnb, mkr, eth, gmx, uni, tia, arb)")
    args = parser.parse_args()

    print("=" * 70)
    print("       CRYPTO TOKENOMICS RATING ENGINE (CLI EDITION)        ")
    print("=" * 70)

    coin_input = args.coin
    if not coin_input:
        coin_input = input("Enter Token Name / Ticker (e.g. BNB, MKR, ETH, GMX, UNI, TIA): ").strip()

    market_data = None
    token_name = coin_input or "Custom Token"
    symbol = "TOKEN"
    profile = None
    financials = None
    treasury = None
    depth = None
    inst_metrics = None

    if coin_input:
        print(f"Fetching market tokenomics for '{coin_input}'...")
        results = api_service.search_tokens(coin_input, limit=1)
        if results:
            selected_coin = results[0]
            cid = selected_coin['id']
            mdata = api_service.fetch_token_market_data(cid)
            if mdata:
                market_data = mdata
                token_name = mdata["name"]
                symbol = mdata["symbol"]
                profile = token_db.get_profile(cid)
                slug = profile.get("defillama_slug") if profile else cid
                financials = api_service.fetch_protocol_financials(slug, mdata.get("market_cap_usd", 0.0)) if slug else None

                t_slug = profile.get("treasury_details", {}).get("defillama_slug") if profile else ""
                fallback_liq = profile.get("treasury_details", {}).get("liquid_stables_usd", 0.0) if profile else 0.0
                fallback_nat = profile.get("treasury_details", {}).get("native_treasury_usd", 0.0) if profile else 0.0
                treasury = api_service.fetch_dao_treasury(t_slug, fallback_liq, fallback_nat)

                next_c_usd = profile.get("unlock_schedule", {}).get("next_cliff_usd", 0.0) if profile else 0.0
                vol_24h = mdata.get("volume_24h_usd", 0.0)
                depth = api_service.fetch_market_depth_and_slippage(symbol, vol_24h, next_c_usd)

                inst_metrics = api_service.compute_institutional_derived_metrics(mdata, profile, financials, treasury, depth)

    if market_data:
        eval_res = scoring.compute_metric_driven_tokenomics(
            market_data,
            profile=profile,
            financials=financials,
            treasury=treasury,
            depth=depth,
            inst_metrics=inst_metrics
        )
        display_report(
            token_name, symbol,
            eval_res["scores"],
            eval_res["composite_score"],
            eval_res["grade_info"],
            market_data=market_data,
            vector_details=eval_res["vector_details"],
            profile=profile,
            financials=financials,
            treasury=treasury,
            depth=depth,
            inst_metrics=inst_metrics,
            warning_badges=eval_res["warning_badges"]
        )
    else:
        print("Proceeding with manual evaluation.")
        v1 = get_float_input("1. Supply Dynamics & Distribution (0-10): ")
        v2 = get_float_input("2. Utility & Demand Drivers (0-10): ")
        v3 = get_float_input("3. Value Accrual Mechanics (0-10): ")
        v4 = get_float_input("4. Ecosystem & Treasury Management (0-10): ")
        v5 = get_float_input("5. Risk Mitigation (0-10): ")
        scores = {"v1": v1, "v2": v2, "v3": v3, "v4": v4, "v5": v5}
        composite_score = scoring.compute_weighted_score(scores)
        grade_info = scoring.calculate_grade(composite_score)
        display_report(token_name, symbol, scores, composite_score, grade_info)


if __name__ == "__main__":
    main()
