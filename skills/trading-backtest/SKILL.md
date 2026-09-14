---
name: trading-backtest
description: Backtest Pine strategies for XAUUSD and EURUSD on Exness-like costs (spread, commission, slippage) with in-sample / out-of-sample discipline.
metadata:
  version: "1.1"
  last_updated: "2026-09-14"
  domain: trading
  pairs: [XAUUSD, EURUSD]
  broker: Exness
  level: intermediate-professional
---

# Trading Backtest — XAUUSD & EURUSD (Exness)

## When to Use
- Pine indicator / strategy live se pehle
- XAUUSD vs EURUSD pe alag results compare
- Parameter change ke baad verify
- Overfitting check

## Core Principles
1. Backtest filter hai, future profit guarantee nahi.
2. Live jaisi costs: **Exness spread + commission + slippage**.
3. XAUUSD aur EURUSD **alag** edge / behaviour — ek ka result doosre pe copy mat karo.
4. In-sample tune, out-of-sample locked.
5. Repaint / lookahead band.

## Broker assumptions (Exness — approximate; apne account se verify)
| Symbol | Typical focus | Cost notes |
|--------|----------------|------------|
| XAUUSD | Gold, faster spikes | Spread wider around news; slippage possible on stops |
| EURUSD | Major FX | Usually tighter spread; still add small slippage |

Backtest properties (example — apni Exness contract / lot specs se match karo):
- Commission: account type ke mutabiq (Raw / Standard)
- Slippage: 1–2 ticks / small fixed (gold pe thoda zyada realistic)
- Position sizing: same method jo live use hogi (fixed lot ya % risk)

## Step-by-step Workflow

### A) Pine Strategy Tester
1. Signals ko `strategy()` rules se map karo (entry/exit clear).
2. Symbol alag-alag run: pehle **XAUUSD**, phir **EURUSD**.
3. Same timeframe jo live chart pe hai.
4. Costs ON (commission + slippage fields).
5. Split:
   - In-sample: older data — tune
   - Out-of-sample: last \~20–30% — no tuning
6. Save: net profit, max DD, profit factor, trade count, equity curve.

### B) Metrics
Net return % | Max DD % | Profit factor | # trades | Win rate | Avg R | Exposure %

### C) Go / No-Go (adjust to your risk)
- OOS positive expectancy dono ya clearly “XAU-only / EUR-only”
- Max DD apni limit ke andar
- OOS pe kaafi trades (masalan 40–50+ jahan possible)
- Exness costs ke baad bhi edge bachi ho
- Paper / small live forward 2–4 weeks

### D) Pair comparison table
| Pair | TF | Trades | Net % | Max DD | PF | OOS ok? | Notes |
|------|----|--------|-------|--------|-----|---------|-------|
| XAUUSD | | | | | | | |
| EURUSD | | | | | | | |

## Anti-patterns
- Zero spread backtest
- Gold pe EUR wale same stop distance (units alag)
- Sirf win rate
- Har din re-optimize
- Ek pair pe full size, doosra untested

## Quality Bar
- [ ] Exness-like costs included
- [ ] XAUUSD + EURUSD alag reports
- [ ] IS / OOS documented
- [ ] Trade list saved
- [ ] Forward test plan

## Sources
- TradingView Strategy Tester
- Exness contract specs / calculator (lot, margin, commission)
- This repo skill: pro-trading-dev-system