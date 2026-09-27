# Institutional Tokenomics & Valuation Safety Engine 🏛️⚡

> **A professional-grade, quantitative tokenomics evaluation and safety scoring platform for digital assets.** Built for venture analysts, hedge funds, DAO researchers, and DeFi allocators.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data: 100% Free Public APIs](https://img.shields.io/badge/Data-Free%20Public%20APIs-orange.svg)](#data-architecture)
[![No API Keys Required](https://img.shields.io/badge/API%20Keys-Zero%20Config-brightgreen.svg)](#quick-start)

---

## 🎯 Overview: Why This Engine Was Built

In traditional equity markets, analysts evaluate free cash flow, operating margin, dilution overhang, and debt runway. In crypto, retail investors are routinely trapped by misleading metrics:

* 🚨 **High FDV / Low Float Traps**: Tokens launching with 5% float and 95% insider unlocks that dump relentlessly over 36 months (e.g. ARB, TIA, STRK).
* 💸 **Fake Yields & Emissions**: Staking yields of 15–20% paid out purely in printed governance tokens, concealing negative real yields (-15% net).
* 👻 **Fee Switch Mirages**: Protocols generating tens of millions in user fees where **0% accrues to tokenholders**, flowing instead into corporate venture accounts or subsidizing LP impermanent loss.
* 💧 **Phantom Liquidity**: Multi-billion-dollar market caps supported by less than \$500k in true on-chain orderbook depth, guaranteeing a 50%+ slippage crash during treasury or unlock liquidations.

The **Institutional Tokenomics Safety Engine** cuts through marketing narratives. It connects to live market data, on-chain orderbook depth, and curated governance registries to compute a comprehensive **0.00 – 10.00 Safety Score** and an institutional grade rating (**AAA** down to **F**).

---

## 🏛️ The 7 Institutional Safety Pillars

Every token is subjected to rigorous quantitative scoring across seven distinct dimensions:

| Dimension | Weight | What It Measures | Red Flags Triggered |
| :--- | :---: | :--- | :--- |
| **1. Net Protocol Margin** | 20% | Protocol Revenue ÷ Total Fees. Does cash accrue to tokenholders or vanish? | Revenue Capture = 0% (Pure governance token) |
| **2. Unlock Cliff & Vesting** | 18% | Circulating ÷ Total Supply, upcoming unlocks, and daily unlock-to-volume ratio. | Float < 30%, unlocks exceeding 5x daily volume |
| **3. Liquid Treasury Runway** | 15% | Liquid Treasury (excluding native token) ÷ Annual Burn Rate. | Runway < 12 months, treasury >80% native illiquid token |
| **4. Orderbook Slippage & Depth** | 14% | Live ±2% orderbook bid/ask depth vs. Market Cap. | Market cap to depth ratio > 500x |
| **5. Real Staking Yield** | 13% | Nominal Staking Yield minus Annual Inflation Rate. | Negative real yield masked by hyper-inflationary rewards |
| **6. Governance Capture Risk** | 10% | Nakamoto coefficient, top-10 holder concentration, foundation veto. | Top 10 control > 60% of voting supply |
| **7. Value Accrual Utility** | 10% | On-chain burn (EIP-1559, Firepit, BEP-95), fee redistribution, staking utility. | Zero token sinks; purely speculative asset |

### Credit-Rating Scale
* **AAA (9.0 – 10.0)**: Sovereign / Ultra-Sound (e.g., BNB, Ethereum post-merge). High real fee burns, massive float, robust liquidity.
* **AA / A (7.5 – 8.9)**: Strong / Investment Grade (e.g., Uniswap post-UNIfication, Maker/Sky, GMX). Active buybacks/burns, clear fee capture.
* **BBB / BB (5.5 – 7.4)**: Moderate Risk / Speculative. Balanced tokenomics with manageable emissions or partial revenue capture.
* **B / CCC (3.5 – 5.4)**: High Fragility. High inflation, low treasury runway, or unverified fee switch status.
* **D / F (< 3.5)**: Extreme Hazard / Predatory Dilution (e.g., early Celestia, unmitigated low-float L2s). Severe unlock cliffs, 0% revenue capture.

---

## 🔬 Featured Case Studies

### 🦄 Uniswap (`UNI`) — The UNIfication Fee Switch & Arbitrage Burn
* **Historic Fee Switch**: The landmark UNIfication governance proposal (Dec 2025) officially activated the protocol fee switch across v2/v3 pools, expanded to v4 and 7 chains (July 2026).
* **The "Firepit" Mechanism**: Protocol fees accumulate in the `TokenJar` contract. External arbitrageurs execute burns of UNI tokens in the `Firepit` to claim the underlying fee assets, creating programmatic buy-and-burn demand.
* **11.2% Genesis Supply Destroyed**: Over **112,217,581 UNI** have been permanently burned to date (including the 100M retroactive treasury burn), reducing total supply from 1.0B to ~887.8M.
* **Safety Grade**: **8.62 / 10.0 (AA — Investment Grade)**.

### 🟡 BNB (`BNB`) — The Gold Standard of Continuous Deflation
* **Hard Supply Reductions**: Auto-Burn protocol and BEP-95 real-time gas burning have permanently reduced max supply from 200,000,000 to ~140,880,000 BNB (**29.56% of total genesis supply burned**).
* **High Net Margin**: Massive real exchange fee discounts and L1 gas settlement utility provide continuous organic demand.
* **Safety Grade**: **9.46 / 10.0 (AAA — Sovereign Sound)**.

### 🔴 High-Float / Predatory Unlocks (`ARB`, `TIA`)
* **Arbitrum (`ARB`)**: ~4.4B circulating out of 10B total supply. Despite generating tens of millions in sequencer fees, L2 sequencer revenue does not accrue to ARB holders, resulting in high unlock overhang and low safety grades.

---

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.9, 3.10, 3.11, or 3.12 installed.

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/tokenomics-analyzer.git
cd tokenomics-analyzer
pip install -r requirements.txt
```

### 3. Launch the Interactive Web Dashboard
#### Windows:
Double-click `run_app.bat` or run:
```cmd
run_app.bat
```

#### macOS / Linux:
```bash
chmod +x run_app.sh
./run_app.sh
```

#### Direct Python Execution:
```bash
python -m streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 💻 CLI Mode (Terminal Quick-Scan)

Perform instant tokenomics scans directly from your terminal:

```bash
# Analyze Uniswap
python tokenomics_analyzer.py --coin uni

# Analyze BNB
python tokenomics_analyzer.py --coin bnb

# Analyze Arbitrum
python tokenomics_analyzer.py --coin arb

# Show detailed breakdown with all 7 dimensions
python tokenomics_analyzer.py --coin mkr --detail
```

**Terminal Output Example**:
```
======================================================================
  INSTITUTIONAL TOKENOMICS SAFETY AUDIT: UNISWAP (UNI)
======================================================================
  Institutional Score : 8.62 / 10.00
  Safety Rating       : [ AA ] - Strong Investment Grade
  Price / Market Cap  : $6.14 / $3.93B
  FDV / Total Supply  : $5.45B / 887.8M UNI
  Burned Supply       : 112,217,581 UNI (11.22% of Genesis Supply)

  SAFETY DIMENSIONS:
    * Net Protocol Margin    : [########--]  8.25/10 (35.0% Revenue Capture)
    * Vesting & Float Overhang: [########--]  8.10/10 (72.1% Circulating)
    * Liquid Runway          : [#########-]  9.50/10 (120+ Months Runway)
    * Orderbook Depth        : [########--]  8.40/10 (0.12% Slippage on $100k)
    * Real Staking Yield     : [########--]  8.80/10 (+5.30% Net Real Yield)
    * Governance Capture Risk: [#########-]  9.00/10 (Low Centralization)
    * Utility & Token Sinks  : [#########-]  9.20/10 (Active Buyback & Burn)

  RISK FLAGS:
    [OK] Fee switch active via UNIfication & Firepit programmatic burn.
    [OK] Deflationary supply pressure verified on-chain.
======================================================================
```

---

## 🔌 Data Architecture & Keyless Operation

The engine operates **100% out of the box** without requiring paid subscriptions or API keys:

```
+-------------------------------------------------------------------------+
|                        PUBLIC DATA PROVIDERS                            |
|                                                                         |
|  +--------------------+  +--------------------+  +--------------------+  |
|  |     CoinGecko      |  |    CoinPaprika     |  |     DeFiLlama      |  |
|  | (Market Cap, Float,|  | (Fast Fallback,    |  | (Fees, Revenue,    |  |
|  |  Prices, Supply)   |  |  Historical Vol)   |  |  Treasury, Yields) |  |
|  +---------+----------+  +---------+----------+  +---------+----------+  |
|            |                       |                       |             |
|            +-----------------------+-----------------------+             |
|                                    |                                     |
|                       +------------v-------------+                       |
|                       |   Binance Public Depth   |                       |
|                       |  (±2% Live Order Depth)  |                       |
|                       +------------+-------------+                       |
+------------------------------------|------------------------------------+
                                     v
+-------------------------------------------------------------------------+
|                  INSTITUTIONAL SCORING ENGINE                           |
|                                                                         |
|  * Curated Governance Profiles (`data/token_profiles.json`)              |
|  * 7-Pillar Quantitative Multi-Vector Model                             |
|  * Automatic Outlier Truncation & Defensive Bounds                      |
+------------------------------------+------------------------------------+
                                     v
+-------------------------------------------------------------------------+
|                     PRESENTATION INTERFACES                             |
|                                                                         |
|        [ Streamlit Web Application ]        [ CLI Auditor Engine ]       |
+-------------------------------------------------------------------------+
```

* **CoinGecko & CoinPaprika**: Real-time prices, circulating floats, and maximum genesis supplies. Automatic fallback handles rate limits seamlessly.
* **DeFiLlama API**: 30-day protocol fees, treasury breakdowns, token holdings, and protocol revenues.
* **Binance Public Depth API**: Live ±2% bid/ask liquidity book to evaluate true market exit capacity.
* **Curated Profile Registry (`data/token_profiles.json`)**: Tracks off-chain and governance-approved parameters (vesting schedules, foundation runway, burn contracts, and fee-switch mechanics).

---

## 📂 Repository Structure

```
TOKENOMICS/
├── .streamlit/
│   └── config.toml             # Institutional dark theme styling
├── data/
│   └── token_profiles.json     # Curated governance & tokenomics parameters
├── api_service.py              # Live multi-source data ingestion & fallbacks
├── app.py                      # Full-featured Streamlit interactive web dashboard
├── scoring.py                  # Institutional quantitative scoring algorithm
├── token_db.py                 # Token database interface & seed profile library
├── tokenomics_analyzer.py      # Standalone CLI analysis utility
├── requirements.txt            # Python package requirements
├── run_app.bat                 # 1-click Windows launcher
├── run_app.sh                  # 1-click Linux/macOS launcher
├── LICENSE                     # MIT License
└── README.md                   # System documentation and user manual
```

---

## ⚖️ License & Disclaimer

**License**: Distributed under the [MIT License](LICENSE).

**Disclaimer**: *This software is an analytical and educational research platform. It does not provide financial, investment, or trading advice. Digital assets are highly volatile and subject to total loss of capital. Always perform independent due diligence.*
