---
name: pro-trading-dev-system
description: Professional developer-trader system for one core Pine indicator on XAUUSD and EURUSD with Exness execution, risk, journal, and weekly review.
metadata:
  version: "1.1"
  last_updated: "2026-09-14"
  domain: trading
  pairs: [XAUUSD, EURUSD]
  broker: Exness
  level: professional
---

# Pro Trading + Dev System — XAUUSD / EURUSD @ Exness

## When to Use
- Daily trading process
- Pine core indicator improve / version
- Risk + journal discipline
- Jarvis se weekly review, checklist, rule text

## Core Principles
1. Ek core Pine edge — har hafte naya system nahi.
2. Sirf **2 pairs**: XAUUSD, EURUSD.
3. Risk pehle; signal baad mein.
4. Pine file versioned; changelog likho.
5. Journal ke bina trade incomplete.
6. Exness pe execution = backtest costs ke qareeb rakhne ki koshish.

## Book definition
| Item | Value |
|------|--------|
| Pairs | XAUUSD, EURUSD |
| Broker | Exness |
| Core tool | Pine Script indicator (your file) |
| Timeframe | (apna TF likho — e.g. M15 / H1) |
| Sessions | Prefer London + NY overlap; gold news pe extra care |

## Signal contract (fill once)
- Entry:
- Confirm: bar close? filter?
- Stop rule:
- Target / RR:
- No-trade: high-impact news (esp. USD, XAU), daily loss hit, already in trade

## Risk (Exness account — numbers example, apni reality se set karo)
| Rule | Suggested start |
|------|------------------|
| Risk per trade | 0.5%–1% |
| Max open risk | ≤ 2% |
| Daily loss stop | 2% — stop trading that day |
| Weekly loss stop | \~5% — reduce size / pause |
| Max positions | 1–2 |

**Gold vs EUR**
- XAUUSD: volatility zyada → stop distance aur lot size carefully; news spikes.
- EURUSD: tighter average conditions → still risk % same methodology.

Rough size idea:
```text
risk_money = account_equity * risk_percent
lot_or_units ≈ risk_money / (stop_distance_in_price * value_per_price_unit)