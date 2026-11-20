# Changelog

## 0.2.0 (2026-11-20) — first release: hardening + the family data plane

### Hardening (V1)
- English-first with `--lang zh` fallback; the comparison table places
  upstream quantstats as the complement (in a pandas notebook, use
  quantstats; in a DSH session, use dsh-quantstats).
- **Honesty envelope** (perf-report/0 artifacts): annualization factor,
  VaR method, sample-size warnings and the period-based caliber live in
  the artifact structure, not print lines; degenerate series refused.
- **Wordlist from the upstream vocabulary** (all period-based, disclosed):
  payoff_ratio, profit_factor, consecutive W/L streaks, ulcer_index + UPI,
  tail_ratio — joining the M0 core.
- Source metadata rides (date range, coverage gaps).

### The family data plane (V2)
- **Committee track-record tearsheet** (`--ledger`): the dsh-TradingAgents
  settled ledger becomes a scorecard in one command — only resolved,
  non-synthetic, directed verdicts score; the caliber states verdict-window
  returns, not daily marks.
- **Series input** (`--series`): any {date, ret} JSON/CSV — jesse backtests,
  kronos artifacts, any engine's shape.
- **Benchmark-relative mode** (`--benchmark`): beta / alpha / excess with
  declared simplifications.

### Packaging
- npm bin + DSH bundle + skill; 23 hermetic checks + CI.

## 0.0.1
Name placeholder.
