"""
API Service Layer for Tokenomics Analyzer
Integrates CoinGecko, CoinPaprika, and DeFiLlama APIs with local caching,
automatic multi-provider fallbacks, tokenomics metric derivations,
and strict upstream rate-limit compliance throttling and cooldowns.
"""

import os
import time
import requests
from collections import deque
from typing import Dict, List, Optional, Any

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINPAPRIKA_BASE = "https://api.coinpaprika.com/v1"
DEFILLAMA_COINS_BASE = "https://coins.llama.fi"
DEFILLAMA_API_BASE = "https://api.llama.fi"

# In-memory cache with TTL to avoid redundant requests
_CACHE: Dict[str, Dict[str, Any]] = {}
DEFAULT_CACHE_TTL = 300  # 5 minutes
DEFAULT_SEARCH_CACHE_TTL = 600  # 10 minutes

_CACHE_STATS = {
    "hits": 0,
    "misses": 0
}

# Default API key (from environment if present)
_CURRENT_API_KEY: str = os.environ.get("COINGECKO_API_KEY", "").strip()


class ProviderRateLimiter:
    """
    Sliding-window request rate limiter with mandatory spacing and HTTP 429 cooldown tracking.
    Enforces upstream API compliance to avoid bans and excessive load.
    """
    def __init__(self, name: str, max_calls: int = 10, period: float = 60.0, min_interval: float = 2.5):
        self.name = name
        self.max_calls = max_calls
        self.period = period
        self.min_interval = min_interval
        self.call_timestamps: deque = deque()
        self.cooldown_until: float = 0.0
        self.last_call_time: float = 0.0

    def set_limits(self, max_calls: int, min_interval: float):
        self.max_calls = max_calls
        self.min_interval = min_interval

    def is_in_cooldown(self) -> bool:
        return time.time() < self.cooldown_until

    def remaining_cooldown(self) -> int:
        return max(0, int(self.cooldown_until - time.time()))

    def prune_old_calls(self):
        now = time.time()
        while self.call_timestamps and (now - self.call_timestamps[0] > self.period):
            self.call_timestamps.popleft()

    def get_recent_calls_count(self) -> int:
        self.prune_old_calls()
        return len(self.call_timestamps)

    def can_call(self) -> bool:
        if self.is_in_cooldown():
            return False
        self.prune_old_calls()
        return len(self.call_timestamps) < self.max_calls

    def throttle(self):
        """Enforce pacing between calls to prevent burst spikes."""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            sleep_needed = self.min_interval - elapsed
            time.sleep(sleep_needed)
        now = time.time()
        self.call_timestamps.append(now)
        self.last_call_time = now

    def trigger_cooldown(self, retry_after: int = 60):
        """Set cooldown period upon receiving an upstream HTTP 429 or rate-limit notice."""
        self.cooldown_until = time.time() + max(10, retry_after)


# Initialize limiters:
# CoinGecko public rate limit is ~10-30 req/min. We default to a safe 10 req/min (3.0s spacing).
# If a Demo API key is configured, rate limit increases to 30 req/min (1.8s spacing).
coingecko_limiter = ProviderRateLimiter(
    name="CoinGecko",
    max_calls=30 if _CURRENT_API_KEY else 10,
    period=60.0,
    min_interval=1.8 if _CURRENT_API_KEY else 3.0
)

# CoinPaprika public rate limit is ~10 req/sec. We pace at safe 0.25s intervals.
coinpaprika_limiter = ProviderRateLimiter(
    name="CoinPaprika",
    max_calls=60,
    period=60.0,
    min_interval=0.25
)

# Fast mapping for common presets to CoinPaprika ticker IDs
PAPRIKA_PRESET_MAP = {
    "binancecoin": "bnb-bnb",
    "bnb": "bnb-bnb",
    "ethereum": "eth-ethereum",
    "eth": "eth-ethereum",
    "bitcoin": "btc-bitcoin",
    "btc": "btc-bitcoin",
    "solana": "sol-solana",
    "sol": "sol-solana",
    "makerdao": "mkr-maker",
    "maker": "mkr-maker",
    "mkr": "mkr-maker",
    "aave": "aave-new",
    "uniswap": "uni-uniswap",
    "uni": "uni-uniswap",
    "gmx": "gmx-gmx",
    "raydium": "ray-raydium",
    "ray": "ray-raydium",
    "hyperliquid": "hype-hyperliquid",
    "hype": "hype-hyperliquid",
    "celestia": "tia-celestia",
    "tia": "tia-celestia",
    "sui": "sui-sui",
    "arbitrum": "arb-arbitrum",
    "arb": "arb-arbitrum",
    "optimism": "op-optimism",
    "op": "op-optimism",
    "pendle": "pendle-pendle",
    "worldcoin-wld": "wld-worldcoin",
    "worldcoin": "wld-worldcoin",
    "wld": "wld-worldcoin",
}


def set_api_key(api_key: str):
    """Set or update the CoinGecko API key dynamically and update compliance limits."""
    global _CURRENT_API_KEY
    _CURRENT_API_KEY = (api_key or "").strip()
    if _CURRENT_API_KEY:
        coingecko_limiter.set_limits(max_calls=30, min_interval=1.8)
    else:
        coingecko_limiter.set_limits(max_calls=10, min_interval=3.0)


def get_api_key() -> str:
    """Return the active CoinGecko API key."""
    return _CURRENT_API_KEY


def get_compliance_stats() -> Dict[str, Any]:
    """Return live rate-limiting, compliance, and caching metrics for the UI."""
    return {
        "coingecko": {
            "name": "CoinGecko",
            "in_cooldown": coingecko_limiter.is_in_cooldown(),
            "cooldown_remaining": coingecko_limiter.remaining_cooldown(),
            "calls_last_minute": coingecko_limiter.get_recent_calls_count(),
            "max_calls": coingecko_limiter.max_calls,
            "min_interval": coingecko_limiter.min_interval,
            "has_key": bool(_CURRENT_API_KEY)
        },
        "coinpaprika": {
            "name": "CoinPaprika",
            "in_cooldown": coinpaprika_limiter.is_in_cooldown(),
            "cooldown_remaining": coinpaprika_limiter.remaining_cooldown(),
            "calls_last_minute": coinpaprika_limiter.get_recent_calls_count(),
            "max_calls": coinpaprika_limiter.max_calls,
        },
        "cache": {
            "hits": _CACHE_STATS["hits"],
            "misses": _CACHE_STATS["misses"],
            "cached_entries": len(_CACHE)
        }
    }


def _get_headers(for_coingecko: bool = False) -> Dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    if for_coingecko and _CURRENT_API_KEY:
        headers["x-cg-demo-api-key"] = _CURRENT_API_KEY
        headers["x-cg-pro-api-key"] = _CURRENT_API_KEY
    return headers


def _get_cached(key: str) -> Optional[Any]:
    if key in _CACHE:
        entry = _CACHE[key]
        if time.time() - entry["timestamp"] < entry["ttl"]:
            _CACHE_STATS["hits"] += 1
            return entry["data"]
        else:
            del _CACHE[key]
    _CACHE_STATS["misses"] += 1
    return None


def _set_cached(key: str, data: Any, ttl: int = DEFAULT_CACHE_TTL):
    _CACHE[key] = {
        "timestamp": time.time(),
        "ttl": ttl,
        "data": data
    }


def search_tokens(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """
    Search tokens by name, ticker, or id.
    Strictly checks rate limits before calling CoinGecko; if at limit or cooling down,
    seamlessly routes to CoinPaprika.
    """
    query = query.strip()
    if not query:
        return []

    cache_key = f"search_{query.lower()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # 1. Try CoinGecko Search (if rate limit budget allows)
    if coingecko_limiter.can_call():
        coingecko_limiter.throttle()
        url = f"{COINGECKO_BASE}/search"
        try:
            response = requests.get(url, params={"query": query}, headers=_get_headers(for_coingecko=True), timeout=6)
            if response.status_code == 200:
                data = response.json()
                raw_coins = data.get("coins", [])
                raw_coins.sort(key=lambda c: (
                    0 if c.get("symbol", "").lower() == query.lower() else (
                        1 if c.get("id", "").lower() == query.lower() else (
                            2 if (c.get("market_cap_rank") and c.get("market_cap_rank") > 0) else 3
                        )
                    ),
                    c.get("market_cap_rank") or 99999
                ))
                coins = raw_coins[:limit]
                results = []
                for c in coins:
                    results.append({
                        "id": c.get("id"),
                        "name": c.get("name"),
                        "symbol": c.get("symbol", "").upper(),
                        "thumb": c.get("thumb"),
                        "market_cap_rank": c.get("market_cap_rank")
                    })
                _set_cached(cache_key, results, ttl=DEFAULT_SEARCH_CACHE_TTL)
                return results
            elif response.status_code == 429:
                retry_h = response.headers.get("Retry-After")
                cd = int(retry_h) if (retry_h and retry_h.isdigit()) else 60
                coingecko_limiter.trigger_cooldown(cd)
                print(f"[Rate Limit Compliance] CoinGecko 429 received. Cooldown {cd}s active.")
        except Exception as e:
            print(f"[API Info] CoinGecko search unavailable ({e}). Falling back.")
    else:
        print("[Rate Limit Compliance] CoinGecko rate limit budget full or cooling down. Routing search to CoinPaprika.")

    # 2. Fallback to CoinPaprika Search
    if coinpaprika_limiter.can_call():
        coinpaprika_limiter.throttle()
        try:
            p_url = f"{COINPAPRIKA_BASE}/search"
            p_resp = requests.get(p_url, params={"q": query, "c": "currencies"}, headers=_get_headers(), timeout=6)
            if p_resp.status_code == 200:
                raw_currencies = p_resp.json().get("currencies", [])
                # Prioritize exact symbol/id matches and higher market cap ranks
                raw_currencies.sort(key=lambda c: (
                    0 if c.get("symbol", "").lower() == query.lower() else (
                        1 if c.get("id", "").lower() == query.lower() else (
                            2 if (c.get("rank") and c.get("rank") > 0) else 3
                        )
                    ),
                    c.get("rank") or 99999
                ))
                currencies = raw_currencies[:limit]
                results = []
                for c in currencies:
                    cid = c.get("id")
                    results.append({
                        "id": cid,
                        "name": c.get("name"),
                        "symbol": c.get("symbol", "").upper(),
                        "thumb": f"https://static.coinpaprika.com/coin/{cid}/logo.png",
                        "market_cap_rank": c.get("rank")
                    })
                _set_cached(cache_key, results, ttl=DEFAULT_SEARCH_CACHE_TTL)
                return results
        except Exception as e:
            print(f"[API Error] CoinPaprika search failed: {e}")

    return []


def fetch_token_market_data(coin_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive market data, supply distribution, and metrics for a given coin_id.
    Fully respects upstream rate limits with pacing and cooldowns.
    """
    coin_id = coin_id.strip().lower()
    cache_key = f"coin_data_{coin_id}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # 1. Try CoinGecko API (only if compliant with rate limit budget and not in cooldown)
    if coingecko_limiter.can_call():
        coingecko_limiter.throttle()
        url = f"{COINGECKO_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }

        try:
            response = requests.get(url, params=params, headers=_get_headers(for_coingecko=True), timeout=7)
            if response.status_code == 200:
                raw = response.json()
                data = _parse_tokenomics_data(raw)
                _set_cached(cache_key, data, ttl=DEFAULT_CACHE_TTL)
                return data
            elif response.status_code == 429:
                retry_h = response.headers.get("Retry-After")
                cd = int(retry_h) if (retry_h and retry_h.isdigit()) else 60
                coingecko_limiter.trigger_cooldown(cd)
                print(f"[Rate Limit Compliance] CoinGecko returned 429. Respecting {cd}s cooldown. Routing to CoinPaprika.")
        except Exception as e:
            print(f"[API Info] CoinGecko fetch failed ({e}). Routing to fallback.")
    else:
        status_msg = f"in cooldown ({coingecko_limiter.remaining_cooldown()}s left)" if coingecko_limiter.is_in_cooldown() else f"at budget ({coingecko_limiter.get_recent_calls_count()}/{coingecko_limiter.max_calls} req/min)"
        print(f"[Rate Limit Compliance] CoinGecko {status_msg}. Routing to CoinPaprika public API.")

    # 2. Try CoinPaprika Fallback (Free, complete data, compliant pacing)
    paprika_data = _fetch_paprika_fallback(coin_id)
    if paprika_data:
        _set_cached(cache_key, paprika_data, ttl=DEFAULT_CACHE_TTL)
        return paprika_data

    # 3. Last Resort: DeFiLlama Fallback
    llama_data = _fetch_llama_fallback(coin_id)
    if llama_data:
        _set_cached(cache_key, llama_data, ttl=180)
        return llama_data

    return None


def _fetch_paprika_fallback(coin_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch full market and supply tokenomics from CoinPaprika with rate limiting compliance.
    """
    if not coinpaprika_limiter.can_call():
        return None

    try:
        # Check direct preset mapping first
        p_id = PAPRIKA_PRESET_MAP.get(coin_id)
        if not p_id:
            coinpaprika_limiter.throttle()
            search_q = coin_id.replace("-wld", "").replace("-", " ")
            s_resp = requests.get(
                f"{COINPAPRIKA_BASE}/search",
                params={"q": search_q, "c": "currencies"},
                headers=_get_headers(),
                timeout=6
            ).json()
            currencies = s_resp.get("currencies", [])
            if currencies:
                p_id = currencies[0]["id"]
                for c in currencies:
                    if c["symbol"].lower() == coin_id.lower() or c["id"].lower() == coin_id.lower():
                        p_id = c["id"]
                        break

        if not p_id:
            return None

        # Fetch ticker data
        coinpaprika_limiter.throttle()
        t_resp = requests.get(f"{COINPAPRIKA_BASE}/tickers/{p_id}", headers=_get_headers(), timeout=7)
        if t_resp.status_code != 200:
            return None
        t_data = t_resp.json()

        quotes = t_data.get("quotes", {}).get("USD", {})
        price_usd = float(quotes.get("price") or 0.0)
        market_cap_usd = float(quotes.get("market_cap") or 0.0)
        volume_24h = float(quotes.get("volume_24h") or 0.0)
        price_change_24h = float(quotes.get("percent_change_24h") or 0.0)
        ath_usd = float(quotes.get("ath_price") or 0.0)
        ath_change_pct = float(quotes.get("percent_from_price_ath") or 0.0)
        rank = int(t_data.get("rank") or 999)

        total_supply = float(t_data.get("total_supply") or 0.0)
        max_supply = float(t_data.get("max_supply") or 0.0) if t_data.get("max_supply") else None

        # Circulating supply calculation
        if price_usd > 0 and market_cap_usd > 0:
            circulating_supply = round(market_cap_usd / price_usd, 2)
        elif total_supply > 0:
            circulating_supply = total_supply
        else:
            circulating_supply = 0.0

        # Check if difference between max_supply and total_supply represents permanently burned tokens
        is_deflationary_burn = (
            coin_id in ["binancecoin", "bnb", "makerdao", "mkr", "uniswap", "uni"] or
            (max_supply and total_supply and max_supply > total_supply and (circulating_supply >= total_supply * 0.98 or (max_supply - total_supply) >= 1_000_000))
        )

        if is_deflationary_burn and max_supply and total_supply and max_supply > total_supply:
            burned_supply = round(max_supply - total_supply, 2)
            burned_pct = round((burned_supply / max_supply) * 100, 2)
            effective_max = total_supply
            fdv_usd = total_supply * price_usd
            float_ratio = min(1.0, round(circulating_supply / total_supply, 4))
            circulating_pct = min(100.0, round((circulating_supply / total_supply) * 100, 2))
            locked_supply = max(0.0, total_supply - circulating_supply)
            locked_usd_value = locked_supply * price_usd
        else:
            burned_supply = 0.0
            burned_pct = 0.0
            effective_max = max_supply if max_supply else (total_supply if total_supply else circulating_supply)
            fdv_usd = (effective_max * price_usd) if (effective_max and price_usd > 0) else market_cap_usd

            # Float Ratio: Market Cap / FDV
            if fdv_usd and fdv_usd > 0 and market_cap_usd > 0:
                float_ratio = min(1.0, round(market_cap_usd / fdv_usd, 4))
            else:
                float_ratio = 1.0

            # Circulating Percentage
            if effective_max and effective_max > 0:
                circulating_pct = min(100.0, round((circulating_supply / effective_max) * 100, 2))
            else:
                circulating_pct = 100.0

            # Locked / Non-circulating supply
            locked_supply = max(0.0, (effective_max or circulating_supply) - circulating_supply)
            locked_usd_value = locked_supply * price_usd

        # Dilution Risk Classification
        if float_ratio >= 0.85:
            risk_level = "Low Dilution Risk"
            supply_score = 9.0
        elif float_ratio >= 0.60:
            risk_level = "Moderate Dilution Risk"
            supply_score = 7.5
        elif float_ratio >= 0.35:
            risk_level = "Elevated Dilution Risk"
            supply_score = 5.5
        elif float_ratio >= 0.15:
            risk_level = "High Dilution Risk (Low Float)"
            supply_score = 3.5
        else:
            risk_level = "Severe Dilution Risk (Heavy Overhang)"
            supply_score = 2.0

        turnover_pct = round((volume_24h / market_cap_usd * 100), 2) if market_cap_usd > 0 else 0.0
        vol_overhang_ratio = round((volume_24h / locked_usd_value), 3) if locked_usd_value > 0 else 999.0

        return {
            "id": coin_id,
            "name": t_data.get("name", coin_id.capitalize()),
            "symbol": t_data.get("symbol", "").upper(),
            "market_cap_rank": rank,
            "price_usd": price_usd,
            "price_change_24h_pct": round(price_change_24h, 2),
            "market_cap_usd": market_cap_usd,
            "fdv_usd": fdv_usd or market_cap_usd,
            "volume_24h_usd": volume_24h,
            "turnover_pct": turnover_pct,
            "circulating_supply": circulating_supply,
            "total_supply": total_supply,
            "max_supply": max_supply,
            "effective_max_supply": effective_max,
            "float_ratio": float_ratio,
            "circulating_pct": circulating_pct,
            "burned_supply": burned_supply,
            "burned_pct": burned_pct,
            "locked_supply": locked_supply,
            "locked_usd_value": locked_usd_value,
            "vol_overhang_ratio": vol_overhang_ratio,
            "dilution_risk_level": risk_level,
            "dilution_risk_score": supply_score,
            "ath_usd": ath_usd,
            "ath_change_pct": round(ath_change_pct, 2),
            "image": f"https://static.coinpaprika.com/coin/{p_id}/logo.png",
            "categories": [],
            "genesis_date": None,
            "description": "Market and supply metrics retrieved via CoinPaprika public API (rate-limit compliant fallback).",
            "source": "CoinPaprika (Public Free Fallback - Rate-Limit Compliant)"
        }
    except Exception as e:
        print(f"[API Error] CoinPaprika fallback failed for {coin_id}: {e}")
        return None


def _fetch_llama_fallback(coin_id: str) -> Optional[Dict[str, Any]]:
    """
    Fallback to DeFiLlama Coins API if CoinGecko and CoinPaprika are unavailable.
    Guarantees all dictionary keys are populated to prevent KeyErrors.
    """
    url = f"{DEFILLAMA_COINS_BASE}/prices/current/coingecko:{coin_id}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=8)
        if resp.status_code == 200:
            res_data = resp.json().get("coins", {}).get(f"coingecko:{coin_id}")
            if res_data:
                price = float(res_data.get("price", 0.0))
                symbol = res_data.get("symbol", "").upper()
                return {
                    "id": coin_id,
                    "name": coin_id.capitalize(),
                    "symbol": symbol,
                    "market_cap_rank": 999,
                    "price_usd": price,
                    "price_change_24h_pct": 0.0,
                    "market_cap_usd": 0.0,
                    "fdv_usd": 0.0,
                    "volume_24h_usd": 0.0,
                    "turnover_pct": 0.0,
                    "circulating_supply": 0.0,
                    "total_supply": 0.0,
                    "max_supply": None,
                    "effective_max_supply": 0.0,
                    "float_ratio": 1.0,
                    "circulating_pct": 100.0,
                    "locked_supply": 0.0,
                    "locked_usd_value": 0.0,
                    "vol_overhang_ratio": 999.0,
                    "dilution_risk_level": "Unknown (Price from DeFiLlama)",
                    "dilution_risk_score": 5.0,
                    "ath_usd": price,
                    "ath_change_pct": 0.0,
                    "image": None,
                    "categories": [],
                    "genesis_date": None,
                    "description": "Retrieved basic price via DeFiLlama fallback due to upstream API rate limits.",
                    "source": "DeFiLlama (Price Fallback)"
                }
    except Exception as e:
        print(f"[API Error] DeFiLlama fallback failed: {e}")
    return None


def fetch_llama_tvl(protocol_slug: str) -> Optional[Dict[str, Any]]:
    """Fetch protocol TVL from DeFiLlama."""
    cache_key = f"llama_tvl_{protocol_slug.lower()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    url = f"{DEFILLAMA_API_BASE}/protocol/{protocol_slug.lower()}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            tvl_data = {
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "tvl": data.get("tvl"),
                "chains": data.get("chains", []),
                "category": data.get("category")
            }
            _set_cached(cache_key, tvl_data, ttl=600)
            return tvl_data
    except Exception:
        pass
    return None


def fetch_protocol_financials(protocol_slug: str, market_cap_usd: float = 0.0) -> Optional[Dict[str, Any]]:
    """
    Fetch live 24h & 30d fees, revenue, annualized run-rates, and valuation multiples
    from DeFiLlama Fees & Revenue API (100% free public endpoint).
    """
    if not protocol_slug:
        return None
    protocol_slug = protocol_slug.strip().lower()
    cache_key = f"llama_fees_{protocol_slug}_{round(market_cap_usd, -6)}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    url = f"https://api.llama.fi/summary/fees/{protocol_slug}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=8)
        if resp.status_code == 200:
            d = resp.json()
            fees_24h = float(d.get("total24h") or 0.0)
            rev_24h = float(d.get("totalRevenue24h") or 0.0)
            fees_30d = float(d.get("total30d") or 0.0)
            rev_30d = float(d.get("totalRevenue30d") or 0.0)
            
            annualized_fees = (fees_30d * 12) if fees_30d > 0 else (fees_24h * 365)
            annualized_rev = (rev_30d * 12) if rev_30d > 0 else (rev_24h * 365)
            
            pf_ratio = round(market_cap_usd / annualized_fees, 1) if (market_cap_usd > 0 and annualized_fees > 0) else None
            ps_ratio = round(market_cap_usd / annualized_rev, 1) if (market_cap_usd > 0 and annualized_rev > 0) else None
            fee_yield = round((annualized_fees / market_cap_usd) * 100, 2) if (market_cap_usd > 0 and annualized_fees > 0) else 0.0

            fin_data = {
                "protocol_slug": protocol_slug,
                "name": d.get("name", protocol_slug.capitalize()),
                "category": d.get("category", "DeFi"),
                "fees_24h_usd": fees_24h,
                "revenue_24h_usd": rev_24h,
                "fees_30d_usd": fees_30d,
                "revenue_30d_usd": rev_30d,
                "annualized_fees_usd": annualized_fees,
                "annualized_revenue_usd": annualized_rev,
                "price_to_fees_ratio": pf_ratio,
                "price_to_sales_ratio": ps_ratio,
                "fee_yield_pct": fee_yield,
                "has_fees": (annualized_fees > 0)
            }
            _set_cached(cache_key, fin_data, ttl=600)
            return fin_data
    except Exception as e:
        print(f"[API Info] Protocol financials fetch failed for {protocol_slug}: {e}")
    return None


def fetch_dao_treasury(
    treasury_slug: str,
    fallback_liquid: float = 0.0,
    fallback_native: float = 0.0
) -> Optional[Dict[str, Any]]:
    """
    Fetch DAO Treasury breakdown from DeFiLlama Treasury API (100% free public endpoint).
    Separates liquid stablecoins/blue-chips from native paper governance tokens.
    """
    if not treasury_slug and fallback_liquid == 0.0 and fallback_native == 0.0:
        return None

    cache_key = f"llama_treasury_{treasury_slug.lower() if treasury_slug else 'fallback'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    if treasury_slug:
        url = f"https://api.llama.fi/treasury/{treasury_slug.lower().strip()}"
        try:
            resp = requests.get(url, headers=_get_headers(), timeout=8)
            if resp.status_code == 200:
                d = resp.json()
                chain_tvls = d.get("currentChainTvls", {})
                
                # OwnTokens represents native governance tokens held in DAO treasury
                native_tokens_usd = float(chain_tvls.get("OwnTokens") or 0.0)
                
                # Sum non-native liquid assets across chains (skip keys with '-OwnTokens' or 'OwnTokens')
                liquid_non_native = 0.0
                for chain_name, val in chain_tvls.items():
                    if "OwnTokens" not in chain_name and isinstance(val, (int, float)):
                        liquid_non_native += float(val)
                
                total_treasury = native_tokens_usd + liquid_non_native
                if total_treasury > 0:
                    native_pct = round((native_tokens_usd / total_treasury) * 100, 1)
                    liquid_pct = round((liquid_non_native / total_treasury) * 100, 1)
                else:
                    native_pct, liquid_pct = 0.0, 100.0

                treasury_data = {
                    "treasury_slug": treasury_slug,
                    "name": d.get("name", treasury_slug.capitalize()),
                    "total_treasury_usd": total_treasury,
                    "native_tokens_usd": native_tokens_usd,
                    "liquid_non_native_usd": liquid_non_native,
                    "native_ratio_pct": native_pct,
                    "liquid_ratio_pct": liquid_pct,
                    "source": "DeFiLlama Live Treasury API",
                    "has_treasury": True
                }
                _set_cached(cache_key, treasury_data, ttl=600)
                return treasury_data
        except Exception as e:
            print(f"[API Info] DeFiLlama treasury fetch failed for {treasury_slug}: {e}")

    # Fallback to curated profile estimates if API failed or no slug
    if fallback_liquid > 0 or fallback_native > 0:
        total = fallback_liquid + fallback_native
        native_pct = round((fallback_native / total) * 100, 1) if total > 0 else 0.0
        liquid_pct = round((fallback_liquid / total) * 100, 1) if total > 0 else 100.0
        fallback_data = {
            "treasury_slug": treasury_slug or "curated",
            "name": treasury_slug.capitalize() if treasury_slug else "Protocol Treasury",
            "total_treasury_usd": total,
            "native_tokens_usd": fallback_native,
            "liquid_non_native_usd": fallback_liquid,
            "native_ratio_pct": native_pct,
            "liquid_ratio_pct": liquid_pct,
            "source": "Institutional Knowledge Store Baseline",
            "has_treasury": True
        }
        _set_cached(cache_key, fallback_data, ttl=600)
        return fallback_data

    return None


def fetch_market_depth_and_slippage(
    symbol: str,
    volume_24h_usd: float = 0.0,
    next_cliff_usd: float = 0.0
) -> Dict[str, Any]:
    """
    Fetch live 2% order book depth from Binance public API or calculate institutional proxy depth.
    Computes the Cliff-to-Depth Slippage Fragility Ratio.
    """
    symbol = (symbol or "").upper().strip()
    cache_key = f"depth_slippage_{symbol}_{round(volume_24h_usd, -4)}_{round(next_cliff_usd, -4)}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    depth_2pct_usd = 0.0
    source = "Institutional Volume-Depth Proxy (~1.2% of 24h Vol)"

    # Try live Binance order book for major pairs
    if symbol and symbol not in ["CUSTOM", "TOKEN"]:
        for quote in ["USDT", "USDC"]:
            pair = f"{symbol}{quote}"
            try:
                resp = requests.get(f"https://api.binance.com/api/v3/depth?symbol={pair}&limit=500", timeout=4)
                if resp.status_code == 200:
                    d = resp.json()
                    bids = d.get("bids", [])
                    asks = d.get("asks", [])
                    if bids and asks:
                        mid_price = (float(bids[0][0]) + float(asks[0][0])) / 2.0
                        bids_2pct = sum(float(p) * float(q) for p, q in bids if float(p) >= mid_price * 0.98)
                        asks_2pct = sum(float(p) * float(q) for p, q in asks if float(p) <= mid_price * 1.02)
                        binance_depth = (bids_2pct + asks_2pct) / 2.0
                        depth_2pct_usd = binance_depth * 2.5
                        source = "Binance Live Order Book (Extrapolated +/-2% Depth)"
                        break
            except Exception:
                pass

    if depth_2pct_usd <= 0 and volume_24h_usd > 0:
        depth_2pct_usd = volume_24h_usd * 0.012

    if depth_2pct_usd > 0 and next_cliff_usd > 0:
        cliff_to_depth_ratio = round(next_cliff_usd / depth_2pct_usd, 2)
    else:
        cliff_to_depth_ratio = 0.0

    if cliff_to_depth_ratio >= 15.0:
        slippage_level = "Catastrophic Fragility (>15x 2% Depth)"
        slippage_badge = "badge-red"
    elif cliff_to_depth_ratio >= 5.0:
        slippage_level = "High Slippage Shock (5x-15x 2% Depth)"
        slippage_badge = "badge-orange"
    elif cliff_to_depth_ratio >= 1.5:
        slippage_level = "Moderate Slippage Shock (1.5x-5x)"
        slippage_badge = "badge-blue"
    elif next_cliff_usd == 0:
        slippage_level = "Zero Cliff Slippage Risk (No Impending Cliff)"
        slippage_badge = "badge-green"
    else:
        slippage_level = "High Depth Buffer (<1.5x 2% Depth)"
        slippage_badge = "badge-green"

    result = {
        "depth_2pct_usd": depth_2pct_usd,
        "cliff_to_depth_ratio": cliff_to_depth_ratio,
        "slippage_level": slippage_level,
        "slippage_badge": slippage_badge,
        "source": source
    }
    _set_cached(cache_key, result, ttl=300)
    return result


def compute_institutional_derived_metrics(
    market_data: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    financials: Optional[Dict[str, Any]] = None,
    treasury: Optional[Dict[str, Any]] = None,
    depth: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes institutional derived metrics:
    - Net Protocol Income & Net Profit Margin %
    - Real Staking APR % (Nominal APR minus Net Inflation Rate)
    - Liquid Stablecoin Runway (Months)
    - Whale / Insider Concentration
    """
    ann_fees = financials.get("annualized_fees_usd", 0.0) if financials else 0.0
    incentives_cfg = profile.get("incentives_and_emissions", {}) if profile else {}
    ann_incentives = float(incentives_cfg.get("annual_token_incentives_usd") or 0.0)
    
    net_income = ann_fees - ann_incentives
    if ann_fees > 0:
        net_margin_pct = round((net_income / ann_fees) * 100, 1)
    elif ann_incentives > 0:
        net_margin_pct = -100.0
    else:
        net_margin_pct = 0.0

    is_mercenary = (net_income < 0 and ann_incentives > 10_000_000) or incentives_cfg.get("is_mercenary_subsidized", False)

    stk = profile.get("staking_details", {}) if profile else {}
    nominal_apr = float(stk.get("nominal_staking_apr_pct") or stk.get("annual_staking_apr_pct") or 0.0)
    
    inf_rate = float(
        incentives_cfg.get("annual_inflation_rate_pct")
        if "annual_inflation_rate_pct" in incentives_cfg
        else (profile.get("unlock_schedule", {}).get("monthly_inflation_rate_pct", 0.0) * 12)
        if profile else 0.0
    )
    real_apr = round(nominal_apr - inf_rate, 2)

    t_cfg = profile.get("treasury_details", {}) if profile else {}
    monthly_burn = float(t_cfg.get("monthly_burn_rate_usd") or 1500000.0)
    liquid_reserves = treasury.get("liquid_non_native_usd", 0.0) if treasury else float(t_cfg.get("liquid_stables_usd") or 0.0)
    
    if monthly_burn > 0:
        runway_months = round(liquid_reserves / monthly_burn, 1)
    else:
        runway_months = 999.0

    major_entities = profile.get("major_entities", []) if profile else []
    top_entities_pct = sum(float(e.get("percentage", 0.0)) for e in major_entities)
    
    insider_pct = sum(
        float(e.get("percentage", 0.0))
        for e in major_entities
        if "public" not in e.get("entity", "").lower() and "retail" not in e.get("entity", "").lower()
    )

    return {
        "annualized_fees_usd": ann_fees,
        "annual_incentives_usd": ann_incentives,
        "net_protocol_income_usd": net_income,
        "net_margin_pct": net_margin_pct,
        "is_mercenary_subsidized": is_mercenary,
        "nominal_staking_apr_pct": nominal_apr,
        "net_inflation_rate_pct": inf_rate,
        "real_staking_apr_pct": real_apr,
        "monthly_burn_rate_usd": monthly_burn,
        "liquid_reserves_usd": liquid_reserves,
        "runway_months": runway_months,
        "top_entities_pct": top_entities_pct,
        "insider_pct": insider_pct,
        "major_entities": major_entities,
        "regulatory": profile.get("regulatory_classification", {}) if profile else {}
    }


def _parse_tokenomics_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse raw CoinGecko coin payload into structured tokenomics data with derived ratios.
    """
    mdata = raw.get("market_data", {})
    
    price_usd = mdata.get("current_price", {}).get("usd") or 0.0
    market_cap_usd = mdata.get("market_cap", {}).get("usd") or 0.0
    fdv_usd = mdata.get("fully_diluted_valuation", {}).get("usd")
    volume_24h = mdata.get("total_volume", {}).get("usd") or 0.0
    
    circulating_supply = mdata.get("circulating_supply") or 0.0
    total_supply = mdata.get("total_supply")
    max_supply = mdata.get("max_supply")
    
    # Check if difference between max_supply and total_supply represents permanently burned tokens
    coin_id = (raw.get("id") or "").lower()
    is_deflationary_burn = (
        coin_id in ["binancecoin", "bnb", "makerdao", "mkr", "uniswap", "uni"] or
        (max_supply and total_supply and max_supply > total_supply and (circulating_supply >= total_supply * 0.98 or (max_supply - total_supply) >= 1_000_000))
    )

    if is_deflationary_burn and max_supply and total_supply and max_supply > total_supply:
        burned_supply = round(max_supply - total_supply, 2)
        burned_pct = round((burned_supply / max_supply) * 100, 2)
        effective_max = total_supply
        fdv_usd = total_supply * price_usd
        float_ratio = min(1.0, round(circulating_supply / total_supply, 4))
        circulating_pct = min(100.0, round((circulating_supply / total_supply) * 100, 2))
        locked_supply = max(0.0, total_supply - circulating_supply)
        locked_usd_value = locked_supply * price_usd
    else:
        burned_supply = 0.0
        burned_pct = 0.0
        # Effective ceiling for tokenomics calculation
        effective_max = max_supply if max_supply else (total_supply if total_supply else circulating_supply)
        
        # If FDV is missing from API, calculate it if effective_max exists
        if not fdv_usd and effective_max and price_usd:
            fdv_usd = effective_max * price_usd
        elif not fdv_usd:
            fdv_usd = market_cap_usd

        # Float Ratio: Market Cap / FDV
        if fdv_usd and fdv_usd > 0 and market_cap_usd > 0:
            float_ratio = min(1.0, round(market_cap_usd / fdv_usd, 4))
        elif effective_max and effective_max > 0 and circulating_supply > 0:
            float_ratio = min(1.0, round(circulating_supply / effective_max, 4))
        else:
            float_ratio = 1.0

        # Circulating Percentage
        if effective_max and effective_max > 0:
            circulating_pct = min(100.0, round((circulating_supply / effective_max) * 100, 2))
        else:
            circulating_pct = 100.0

        # Locked / Non-circulating supply
        locked_supply = max(0.0, (effective_max or circulating_supply) - circulating_supply)
        locked_usd_value = locked_supply * price_usd

    # Dilution Risk Classification & heuristic supply score
    if float_ratio >= 0.85:
        risk_level = "Low Dilution Risk"
        supply_score = 9.0
    elif float_ratio >= 0.60:
        risk_level = "Moderate Dilution Risk"
        supply_score = 7.5
    elif float_ratio >= 0.35:
        risk_level = "Elevated Dilution Risk"
        supply_score = 5.5
    elif float_ratio >= 0.15:
        risk_level = "High Dilution Risk (Low Float)"
        supply_score = 3.5
    else:
        risk_level = "Severe Dilution Risk (Heavy Overhang)"
        supply_score = 2.0

    # Price change and ATH metrics
    price_change_24h = mdata.get("price_change_percentage_24h") or 0.0
    ath_usd = mdata.get("ath", {}).get("usd") or 0.0
    ath_change_pct = mdata.get("ath_change_percentage", {}).get("usd") or 0.0

    # Description (clean plain text preview)
    raw_desc = raw.get("description", {}).get("en", "")
    clean_desc = raw_desc.split(". ")[0] + "." if raw_desc else ""

    market_cap_rank = raw.get("market_cap_rank") or mdata.get("market_cap_rank") or 999
    turnover_pct = round((volume_24h / market_cap_usd * 100), 2) if market_cap_usd > 0 else 0.0
    vol_overhang_ratio = round((volume_24h / locked_usd_value), 3) if locked_usd_value > 0 else 999.0

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "symbol": raw.get("symbol", "").upper(),
        "market_cap_rank": market_cap_rank,
        "price_usd": price_usd,
        "price_change_24h_pct": round(price_change_24h, 2),
        "market_cap_usd": market_cap_usd,
        "fdv_usd": fdv_usd or market_cap_usd,
        "volume_24h_usd": volume_24h,
        "turnover_pct": turnover_pct,
        "circulating_supply": circulating_supply,
        "total_supply": total_supply,
        "max_supply": max_supply,
        "effective_max_supply": effective_max,
        "float_ratio": float_ratio,
        "circulating_pct": circulating_pct,
        "burned_supply": burned_supply,
        "burned_pct": burned_pct,
        "locked_supply": locked_supply,
        "locked_usd_value": locked_usd_value,
        "vol_overhang_ratio": vol_overhang_ratio,
        "dilution_risk_level": risk_level,
        "dilution_risk_score": supply_score,
        "ath_usd": ath_usd,
        "ath_change_pct": round(ath_change_pct, 2),
        "image": raw.get("image", {}).get("large") or raw.get("image", {}).get("small"),
        "categories": raw.get("categories", [])[:4],
        "genesis_date": raw.get("genesis_date"),
        "description": clean_desc,
        "source": "CoinGecko Live API"
    }
