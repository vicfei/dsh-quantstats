# dsh-quantstats — performance tearsheets for DeepSeek Harness, honesty included

**Sharpe, Sortino, Calmar, drawdown, VaR — computed deterministically from your
returns, rendered as a zero-dependency SVG tearsheet, with the assumptions
disclosed and the sample-size alarm on. The report that states its own limits.**

[English](README.md) | [简体中文](README.zh-CN.md)

[![DeepSeek Harness](https://img.shields.io/badge/DSH-plugin-4E6DD4)](https://github.com/deepseek-ai) [![License: MIT](https://img.shields.io/badge/license-MIT-3da639)](LICENSE) [![QuantStats Apache-2.0](https://img.shields.io/badge/concept-QuantStats%20Apache--2.0-35a7a0)](https://github.com/ranaroussi/quantstats)

> Implements the core concept of [QuantStats](https://github.com/ranaroussi/quantstats)
> (7.9k★, by the yfinance author) natively for DSH. Not affiliated.
> Family: [dsh-TradingAgents](https://github.com/vicfei/dsh-TradingAgents) ·
> [dsh-ai-hedge-fund](https://github.com/vicfei/dsh-ai-hedge-fund) ·
> [dsh-Vibe-Trading](https://github.com/vicfei/dsh-Vibe-Trading) ·
> [dsh-OpenBB](https://github.com/vicfei/dsh-OpenBB) · [dsh-CCXT](https://github.com/vicfei/dsh-CCXT) ·
> [dsh-nautilus_trader](https://github.com/vicfei/dsh-nautilus_trader) ·
> [dsh-hummingbot](https://github.com/vicfei/dsh-hummingbot) · [dsh-jesse](https://github.com/vicfei/dsh-jesse).


## Where upstream quantstats fits (a complement, not a competitor)

Upstream [quantstats](https://github.com/ranaroussi/quantstats) (7.9k★, by the
yfinance author) is a completed-state Python library for notebook quants:
~60 metrics, 20 plots, HTML tearsheets, a heavy stack (pandas/scipy/
matplotlib/seaborn/yfinance). **In a pandas notebook, use quantstats.**
dsh-quantstats is the **DSH-session report layer**: zero-dependency, every
metric rides with its caliber (period-based, disclosed), inline-SVG
tearsheets, family-artifact consumption (committee ledgers, engine series).

| | upstream quantstats (complement) | **dsh-quantstats** |
|---|---|---|
| Form | Python library for notebooks | **DSH plugin** — agent asks, report out |
| Deps | pandas/scipy/matplotlib/seaborn/yfinance | **zero (stdlib only)** |
| Calibers | period-vs-trade disclosure in README | **every metric carries its caliber line in-band** |
| Data | yfinance downloads | **your series / family artifacts** |

## Why (QuantStats exists — what does the DSH-native version add?)

| | QuantStats library | **dsh-quantstats** |
|---|---|---|
| Runs where | Python lab / notebooks | **DSH in-session** — agents tearsheet any family engine's output |
| Report | matplotlib HTML (CDN deps) | **zero-dependency inline SVG** — offline, shareable |
| Assumptions | stated in docs | **stated on every report**: annualization factor, historical-VaR method |
| Small samples | — | **sample-size alarm**: n<30 flags Sharpe/Sortino as noise |

## Quick start

```bash
git clone https://github.com/vicfei/dsh-quantstats && cd dsh-quantstats
python3 scripts/tearsheet.py --data <klines.json> --save                 # buy & hold
python3 scripts/tearsheet.py --data <klines.json> --strategy sma --fast 20 --slow 60 --save
```

Real smoke (binance BTC/USDT 365d, 2026-11-17) — the bear-year in one table:

| | buy & hold | SMA 20/60 |
|---|---|---|
| total | −29.9% | **+1.6%** |
| vol(ann) | 44.3% | 25.9% |
| max DD | −39.5% | −19.3% |
| Sharpe | −0.58 | 0.19 |

Assumptions disclosed on both (annualization=365, historical VaR, n=364).

## Status & roadmap

v0 tearsheet engine smoke-tested on live data. [ROADMAP](ROADMAP.md): M1 rolling
metrics + benchmark-relative mode; M2 plugin form; M3 report standard.

## License & disclaimer

MIT; concept inspired by Apache-2.0 upstream — no upstream code used.
**Not investment advice.** Past performance ≠ future results.
