---
name: dsh-quantstats
description: Performance tearsheets for DeepSeek Harness — Sharpe/Sortino/Calmar/drawdown/VaR computed deterministically, zero-dependency SVG reports, assumptions and sample-size alarms on every output.
---

Use this skill when asked to evaluate strategy/portfolio performance
("表现怎么样", "夏普多少", "回撤多大", "出个报告"). The engine is deterministic —
you feed returns, it reports with the limits stated.

## Run

```bash
KIT=<this-directory>
python3 $KIT/scripts/tearsheet.py --data <klines.json> --save
python3 $KIT/scripts/tearsheet.py --data <klines.json> --strategy sma --fast 20 --slow 60 --save
```

K-lines JSON: {"SYMBOL": [[date, open, close, high, low, volume], ...]}.

## Discipline

- Never quote Sharpe/Sortino without the annualization factor and sample size;
  n<30 must be flagged as noise.
- VaR is historical/non-parametric — say so when citing.
- The HTML report is self-contained (no CDN) — safe to share.
- Not investment advice.
