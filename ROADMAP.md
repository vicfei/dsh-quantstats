# ROADMAP — dsh-quantstats

North star: the family's performance-report seat, riding the QuantStats 7.9k★
gravity, 100–300★ in 30 days. Naming on all surfaces: GitHub = npm =
dsh-quantstats (mirrors the upstream lowercase name). Family division:
nautilus = backtests · jesse = tuning · **this repo = measurement and
reporting** — every family engine's output should flow through here to get
one honest scorecard.

## Positioning discipline (this repo's own)

Upstream [QuantStats](https://github.com/ranaroussi/quantstats) is a
**completed-state library** (7.5 years, yfinance author, quality-fix-only
maintenance): a Python API with a heavy stack (pandas/scipy/matplotlib/
seaborn/yfinance) for notebook quants. It will never be an agent product.
We are the **DSH-session report layer**: zero-dependency, every metric
rides with its caliber, SVG tearsheets, family-artifact consumption.
The README table says it plainly: **in a pandas notebook, use quantstats;
in a DSH session, use dsh-quantstats** (the jesse-seat complement pattern,
third application).

**Competitive read (2026-11-20 deep-dive, issue #1)**: upstream's own README
carries a caliber disclosure (period-based vs trade-based metrics) — the
honesty-trio soul is validated, not differentiated alone; our wordlist
adopts from its ~60-metric vocabulary, each with the period caliber stated.
Its Monte Carlo family defers to the family bridge (dsh-Kronos) per
division of labor — we measure, Kronos simulates.

## Milestones

### M0 ✅ (2026-11-17)
Tearsheet engine (sharpe/sortino/calmar/drawdown/VaR/CVaR/skew/win-rate +
zero-dependency SVG equity & drawdown curves + the honesty trio:
annualization-factor disclosure / historical-VaR declaration / sample-size
alerts). Real smoke: BTC 365d bear-year double table (buy&hold −29.9%/DD
−39.5% vs SMA20/60 +1.6%/−19.3%).

### V1 · Hardening + release train ✅ (2026-11-20)
- [x] V1.1 EN-first: engine output via i18n table (en default, `--lang zh`
      fallback); README pure EN with the upstream-complement table +
      `README.zh-CN.md` translation
- [x] V1.2 honesty envelope: the trio becomes structural (annualization
      factor, VaR method, sample-size warnings inside the saved artifact,
      schema perf-report/0); unavailable-with-reason on degenerate series
- [x] V1.3 source metadata rides: data origin/date-range/periods/coverage
- [x] V1.4 **wordlist expansion from the upstream vocabulary, each with its
      caliber**: payoff_ratio / profit_factor / consecutive_wins_losses /
      ulcer_index / tail_ratio / best / worst — all period-based, disclosed
- [x] V1.5 release train: root package (bin shim, dsh.bundle + skill,
      hermetic tests + CI, `scripts/*.py` glob); owner publish;
      awesome-dsh submission

### V2 · The family data plane ✅ (2026-11-20 → npm 0.2.0)
- [x] V2.1 **the committee track-record tearsheet**: consume the
      dsh-TradingAgents settled ledger (verdict returns → return series →
      tearsheet) — "the committee's scorecard, one command"; period-based
      caliber stated; synthetic entries marked, never mixed
- [x] V2.2 family-engine consumption: jesse backtest summaries, kronos
      objectives, any {date, ret} series (JSON/CSV) → tearsheet
- [x] V2.3 benchmark-relative mode: excess return / alpha / beta vs a
      benchmark series, with the same honesty trio

### V3 · Depth + plugin form (0.3.x)
- [ ] V3.1 rolling metrics (rolling Sharpe / drawdown curves as SVG)
- [ ] V3.2 typed tools for the DSH host (tearsheet_run / metrics_compute)
- [ ] V3.3 PERF-REPORT spec v0.1 (the family's interchange formats:
      IC-MEMO · RESEARCH-TRAIL · OPT-REPORT · SCENARIO-REPORT · PERF-REPORT)

## Star strategy

1. Name = traffic (`quantstats`); topics carry dsh/dsh-plugin.
2. Hook: **"every metric rides with its caliber — the tearsheet that tells
   you what its numbers mean"**; the committee-scorecard tearsheet (V2.1)
   doubles as the family-loop showcase.
3. The bear-year double table is post-ready.
4. awesome-dsh submission after npm 0.1.0; family combo discipline.

## Discipline (non-negotiable)

- The honesty trio (annualization factor / VaR method / sample-size alerts)
  never detaches from any output.
- Metrics are descriptive statistics, never phrased as predictions; every
  trade-statistic carries its period-based caliber; no investment advice.
