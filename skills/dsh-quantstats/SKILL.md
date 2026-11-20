---
name: dsh-quantstats
description: Performance tearsheets for DeepSeek Harness — zero-dependency, every metric rides with its period-based caliber, the honesty trio (annualization / VaR method / sample-size) structural in every artifact; consumes family artifacts (committee track records, engine series) and renders inline-SVG tearsheets.
---

Use this skill when asked to measure/report performance ("tearsheet this",
"how did the strategy do", "sharpe of this series", "the committee's
scorecard"). Deterministic — you orchestrate, it computes. Requires python3
(stdlib only).

## Run

```bash
dsh-quantstats --data <klines.json>                              # buy&hold tearsheet
dsh-quantstats --data klines.json --strategy sma --fast 20 --slow 60 --save
dsh-quantstats --series <returns.json>                           # any {date,ret} series
dsh-quantstats --ledger ~/dsh-tradingagents/memos/ledger.json    # committee scorecard
dsh-quantstats --data klines.json --benchmark bench.json         # relative mode
```

## Discipline

- The honesty trio never detaches; metrics are descriptive statistics, never
  forecasts; every trade statistic is period-based, disclosed.
- In a pandas notebook, point users to upstream quantstats — the complement.
