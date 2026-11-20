#!/usr/bin/env python3
"""Performance tearsheet engine (the quantstats concept seat, native implementation)

Upstream QuantStats (7.9k★, Apache-2.0, by the yfinance author) is a
completed-state library for notebook quants: ~60 metrics, 20 plots, HTML
tearsheets over a heavy stack. This plugin is the **DSH-session report
layer** — zero-dependency, every metric rides with its caliber, inline-SVG
tearsheets, family-artifact consumption. In a pandas notebook, use
quantstats; in a DSH session, use dsh-quantstats.

The honesty trio (never detaches):
- annualization factor disclosed explicitly (crypto 365 / equities 252,
  parameterized)
- sample-size warnings on Sharpe/Sortino when n < 30 (noise zone)
- VaR declared historical non-parametric; "past performance ≠ future"
  written into the output itself

Usage:
  python3 scripts/tearsheet.py --data /tmp/btc_365.json                  # buy&hold
  python3 scripts/tearsheet.py --data /tmp/btc_365.json --strategy sma --fast 20 --slow 60 --save
"""
import argparse, datetime as dt, json, math, os, sys

# English is the first language (family rule); Chinese is the --lang zh fallback.
LANG = "en"
STR = {
    "en": {
        "header": "## Tearsheet · {label}",
        "honesty_title": "## Honesty trio (assumptions & warnings, never detaches)",
        "honesty_lines": [
            "annualization factor = {ppy} ({kind} daily, a parameterized assumption — change the frequency, change the factor)",
            "VaR/CVaR are historical non-parametric quantiles; no tail-distribution assumption is made",
            "sample size {n}{warn}",
            "past performance ≠ future results; this table is descriptive statistics, not a forecast",
        ],
        "noise_warn": " ⚠ <30: Sharpe/Sortino are in the noise zone — not comparable",
        "ppy_kind_crypto": "crypto",
        "ppy_kind_equity": "equities",
        "footer": "engine: tearsheet v0 · zero-dependency SVG · {ts} · not investment advice",
        "saved": "→ {path}",
        "win_rate_label": "win_rate(periods)",
        "payoff_label": "payoff_ratio(periods)",
        "annualized": "ann",
    },
    "zh": {
        "header": "## Tearsheet · {label}",
        "honesty_title": "## 诚实件（假设与警告，不可剥离）",
        "honesty_lines": [
            "年化因子 = {ppy}（{kind}日频，参数化假设，换频率须换因子）",
            "VaR/CVaR 为历史非参数分位数，不含尾部分布假设",
            "样本量 {n}{warn}",
            "过去业绩≠未来表现；本表为描述统计，非预测",
        ],
        "noise_warn": " ⚠ <30：Sharpe/Sortino 处于噪声区，不可用于比较",
        "ppy_kind_crypto": "加密",
        "ppy_kind_equity": "股票",
        "footer": "engine: tearsheet v0 · 零依赖 SVG · {ts} · 非投资建议",
        "saved": "→ {path}",
        "win_rate_label": "胜率(按期)",
        "payoff_label": "盈亏比(按期)",
        "annualized": "年化",
    },
}


def t(key, **kw):
    s0 = STR[LANG].get(key, key)
    if isinstance(s0, list):
        return [x.format(**kw) for x in s0]
    return s0.format(**kw) if kw else s0


def metrics(rets, periods_per_year, label):
    n = len(rets)
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / (n - 1)
    std = var ** 0.5
    downside = [r for r in rets if r < 0]
    dstd = (sum(r * r for r in downside) / max(len(downside), 1)) ** 0.5
    total = 1.0
    eq = []
    for r in rets:
        total *= 1 + r
        eq.append(total)
    years = n / periods_per_year
    cagr = total ** (1 / years) - 1 if years > 0 else 0.0
    peak, mdd = eq[0], 0.0
    dd_series = []
    for e in eq:
        peak = max(peak, e)
        dd_series.append(e / peak - 1)
        mdd = min(mdd, e / peak - 1)
    srt = sorted(rets)
    var5 = srt[max(0, int(0.05 * n) - 1)]
    cvar5 = sum(srt[: max(1, int(0.05 * n))]) / max(1, int(0.05 * n))
    skew = (n / ((n - 1) * (n - 2)) * sum(((r - mean) / std) ** 3 for r in rets)) if n > 2 and std > 0 else 0.0
    wins = [r for r in rets if r > 0]
    losses = [r for r in rets if r < 0]
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    payoff = avg_win / abs(avg_loss) if avg_loss != 0 else 0.0
    profit_factor = sum(wins) / abs(sum(losses)) if losses and sum(losses) != 0 else 0.0
    cons_win = cons_loss = cw = cl = 0
    for r in rets:
        if r > 0:
            cw += 1; cl = 0
        elif r < 0:
            cl += 1; cw = 0
        cons_win = max(cons_win, cw); cons_loss = max(cons_loss, cl)
    ulcer = (sum(d * d for d in dd_series) / n) ** 0.5
    p95 = srt[min(int(0.95 * n), n - 1)]
    p05 = srt[max(0, int(0.05 * n) - 1)]
    tail_ratio = p95 / abs(p05) if p05 != 0 else 0.0
    return {"label": label, "periods": n, "total_return": total - 1, "cagr": cagr,
            "payoff_ratio_periods": payoff, "profit_factor": profit_factor,
            "consecutive_wins_periods": cons_win, "consecutive_losses_periods": cons_loss,
            "ulcer_index": ulcer, "ulcer_performance_index": cagr / ulcer if ulcer > 0 else 0.0,
            "tail_ratio": tail_ratio,
            "vol_annualized": std * math.sqrt(periods_per_year),
            "sharpe": mean / std * math.sqrt(periods_per_year) if std > 0 else 0.0,
            "sortino": mean / dstd * math.sqrt(periods_per_year) if dstd > 0 else 0.0,
            "calmar": cagr / abs(mdd) if mdd < 0 else 0.0,
            "max_drawdown": mdd, "var5_hist": var5, "cvar5_hist": cvar5,
            "win_rate_periods": sum(1 for r in rets if r > 0) / n,
            "skew": skew, "best_period": max(rets), "worst_period": min(rets),
            "equity_curve": eq, "_dd_series": dd_series}


def coverage_gaps(bars, threshold=10):
    gaps = []
    for i in range(1, len(bars)):
        try:
            a = dt.date.fromisoformat(str(bars[i - 1][0])[:10])
            b = dt.date.fromisoformat(str(bars[i][0])[:10])
        except ValueError:
            continue
        if (b - a).days > threshold:
            gaps.append({"from": str(bars[i - 1][0])[:10], "to": str(bars[i][0])[:10],
                         "calendar_days": (b - a).days})
    return gaps


def check_preconditions(rets):
    problems = []
    if len(rets) < 10:
        problems.append(f"insufficient series: {len(rets)} periods, need >= 10")
    if any(not math.isfinite(r) for r in rets):
        problems.append("non-finite return in series")
    if len(set(rets)) == 1:
        problems.append("zero-variance series — every ratio metric is undefined")
    return problems


def klines_to_returns(bars):
    closes = [b[2] for b in bars]
    return [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))], bars[1:]


def strategy_returns(bars, fast, slow, fee_bps):
    closes = [b[2] for b in bars]
    def sma(xs, n):
        out, s = [], 0.0
        for i, x in enumerate(xs):
            s += x
            if i >= n: s -= xs[i - n]
            out.append(s / n if i >= n - 1 else None)
        return out
    f, s = sma(closes, fast), sma(closes, slow)
    fee = fee_bps / 10000
    pos, rets = 0, []
    for i in range(1, len(bars)):
        r = closes[i] / closes[i - 1] - 1
        if f[i] is not None and s[i] is not None:
            if pos == 0 and f[i] > s[i]:
                pos = 1; r = r - fee
            elif pos == 1 and f[i] < s[i]:
                pos = 0; r = r - fee
        rets.append(r if pos == 1 else 0.0)
    return rets, bars[1:]


ENVELOPE_PPY = '?'


def svg_equity(eq, dates, title, w=720, h=200):
    lo, hi = min(eq), max(eq)
    n = len(eq)
    X = lambda i: 40 + i * (w - 60) / (n - 1)
    Y = lambda v: 20 + (hi - v) * (h - 60) / (hi - lo + 1e-9)
    path = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(eq))
    peak_path, peak = [], eq[0]
    for i, v in enumerate(eq):
        peak = max(peak, v)
        peak_path.append(f"{X(i):.1f},{Y(peak):.1f}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="monospace">'
            f'<text x="10" y="14" font-size="12">{title} · net {eq[-1]:.4f} (start=1)</text>'
            f'<polyline points="{" ".join(peak_path)}" fill="none" stroke="#aaa" stroke-dasharray="3,3"/>'
            f'<polyline points="{path}" fill="none" stroke="#2456c4" stroke-width="1.5"/>'
            f'<text x="10" y="{h-6}" font-size="10" fill="#567">{dates[0]} → {dates[-1]} · {n} periods · dashed=running peak · ann={ENVELOPE_PPY}</text></svg>')


def svg_drawdown(dds, dates, w=720, h=140):
    n = len(dds)
    lo = min(dds)
    X = lambda i: 40 + i * (w - 60) / (n - 1)
    Y = lambda v: 16 + v / (lo + 1e-9) * (h - 46)  # v∈[lo,0] → [h-30,16]
    path = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(dds))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="monospace">'
            f'<text x="10" y="12" font-size="12">Drawdown · max {lo:.1%}</text>'
            f'<polyline points="{path}" fill="none" stroke="#c23531" stroke-width="1.2"/>'
            f'<line x1="40" y1="16" x2="{w-20}" y2="16" stroke="#ccc"/>'
            f'<text x="10" y="{h-6}" font-size="10" fill="#567">{dates[0]} → {dates[-1]}</text></svg>')


def load_series(path):
    """any {date, ret} input: JSON list [{date, ret}] or CSV date,ret (V2.2)"""
    if path.endswith(".csv"):
        rows = []
        for line in open(path).read().strip().split("\n")[1:]:
            d, r = line.split(",")[:2]
            rows.append({"date": d.strip(), "ret": float(r)})
        return rows
    return json.load(open(path))


def load_ledger(path):
    """dsh-TradingAgents settled ledger -> directed-verdict return series (V2.1).
    Only resolved, non-synthetic, directed entries count; pending and synthetic
    are reported and excluded. Caliber: verdict-window returns (holding-period
    holds), not daily marks."""
    d = json.load(open(path))
    entries = d.get("entries", d if isinstance(d, list) else [])
    rows, pending, synthetic, unscored = [], 0, 0, 0
    for e in entries:
        if e.get("synthetic"):
            synthetic += 1
            continue
        if e.get("pending", True):
            pending += 1
            continue
        ret = e.get("settled_return")
        if ret is None or e.get("decision") in ("PASS", "REVIEW"):
            unscored += 1
            continue
        rows.append({"date": e.get("resolution_date") or e.get("date"), "ret": float(ret)})
    rows.sort(key=lambda r: r["date"])
    return rows, {"pending": pending, "synthetic_excluded": synthetic,
                  "resolved_unscored": unscored, "scored": len(rows),
                  "caliber": "verdict-window returns (holding-period holds), not daily marks"}


def relative_metrics(rets, bench_rets, periods_per_year):
    """benchmark-relative block (V2.3): excess / alpha / beta, period-based."""
    n = min(len(rets), len(bench_rets))
    if n < 10:
        return {"unavailable": f"overlapping periods {n} < 10"}
    r, b = rets[-n:], bench_rets[-n:]
    mr, mb = sum(r) / n, sum(b) / n
    cov = sum((r[i] - mr) * (b[i] - mb) for i in range(n)) / (n - 1)
    vb = sum((b[i] - mb) ** 2 for i in range(n)) / (n - 1)
    beta = cov / vb if vb > 0 else 0.0
    excess = [r[i] - b[i] for i in range(n)]
    me = sum(excess) / n
    return {"beta_period_based": beta, "mean_excess_period": me,
            "alpha_annualized": me * periods_per_year,
            "excess_total": (math.prod(1 + x for x in excess) - 1) if excess else 0.0,
            "overlapping_periods": n,
            "caliber": "beta = cov/var on overlapping periods; alpha = mean excess x annualization factor (a simplification, not a factor model)"}


def render_rows(m):
    return [("periods", m["periods"]), ("total_return", f"{m['total_return']:+.2%}"),
            ("CAGR", f"{m['cagr']:+.2%}"), ("vol(ann)", f"{m['vol_annualized']:.2%}"),
            ("sharpe", f"{m['sharpe']:.2f}"), ("sortino", f"{m['sortino']:.2f}"),
            ("calmar", f"{m['calmar']:.2f}"), ("max_drawdown", f"{m['max_drawdown']:.1%}"),
            ("VaR5(hist)", f"{m['var5_hist']:.2%}"), ("CVaR5(hist)", f"{m['cvar5_hist']:.2%}"),
            (t("win_rate_label"), f"{m['win_rate_periods']:.1%}"), ("skew", f"{m['skew']:.2f}"),
            ("best/worst period", f"{m['best_period']:+.2%} / {m['worst_period']:+.2%}"),
            (t("payoff_label"), f"{m['payoff_ratio_periods']:.2f}"),
            ("profit_factor", f"{m['profit_factor']:.2f}"),
            ("consecutive W/L (periods)", f"{m['consecutive_wins_periods']} / {m['consecutive_losses_periods']}"),
            ("ulcer_index", f"{m['ulcer_index']:.4f}"), ("UPI", f"{m['ulcer_performance_index']:.2f}"),
            ("tail_ratio (P95/|P5|)", f"{m['tail_ratio']:.2f}")]


def main():
    global LANG
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="klines JSON (required unless --series/--ledger)")
    ap.add_argument("--strategy", choices=("buyhold", "sma"), default="buyhold")
    ap.add_argument("--fast", type=int, default=20)
    ap.add_argument("--slow", type=int, default=60)
    ap.add_argument("--fee_bps", type=float, default=5)
    ap.add_argument("--periods_per_year", type=int, default=365, help="crypto=365 equities=252 (disclosed)")
    ap.add_argument("--series", help="any {date, ret} series: JSON list or CSV (family engines emit this shape)")
    ap.add_argument("--ledger", help="dsh-TradingAgents ledger JSON -> the committee scorecard")
    ap.add_argument("--benchmark", help="benchmark series ({date, ret} JSON/CSV or klines JSON) for relative mode")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--lang", choices=("en", "zh"), default="en",
                    help="output language (default en; zh is the fallback)")
    args = ap.parse_args()
    LANG = args.lang
    if not (args.data or args.series or args.ledger):
        sys.exit("refused honestly -- one of --data / --series / --ledger is required")
    ledger_note = ""
    if args.ledger:
        rows_l, ledger_stats = load_ledger(args.ledger)
        rets = [r["ret"] for r in rows_l]
        dated = [[r["date"], 0, 0, 0, 0, 0] for r in rows_l]
        symbol = "committee"
        label = f"committee track record ({ledger_stats['scored']} scored verdicts)"
        ledger_note = (f"ledger: {ledger_stats['scored']} scored | {ledger_stats['pending']} pending | "
                       f"{ledger_stats['synthetic_excluded']} synthetic excluded | {ledger_stats['resolved_unscored']} resolved-unscored"
                       f" | caliber: {ledger_stats['caliber']}")
        bars = dated
    elif args.series:
        rows_s = load_series(args.series)
        rets = [r["ret"] for r in rows_s]
        dated = [[r.get("date", str(i)), 0, 0, 0, 0, 0] for i, r in enumerate(rows_s)]
        symbol = "series"
        label = f"series {os.path.basename(args.series)}"
        bars = dated
    else:
        data = json.load(open(args.data))
        symbol, bars = next(iter(data.items()))
    if not args.ledger and not args.series and args.strategy == "sma":
        rets, dated = strategy_returns(bars, args.fast, args.slow, args.fee_bps)
        label = f"{symbol} SMA{args.fast}/{args.slow} (fee {args.fee_bps}bps)"
    elif not args.ledger and not args.series:
        rets, dated = klines_to_returns(bars)
        label = f"{symbol} buy&hold"
    problems = check_preconditions(rets)
    if problems:
        sys.exit("refused honestly — " + "; ".join(problems))
    m = metrics(rets, args.periods_per_year, label)
    dates = [b[0] for b in dated]
    gaps = coverage_gaps(bars)
    source = {"origin": "user-provided klines JSON", "symbol": symbol,
              "date_range": [str(bars[0][0])[:10], str(bars[-1][0])[:10]],
              "bars": len(bars), "coverage_gaps": gaps}

    relative = None
    if args.benchmark:
        bd = json.load(open(args.benchmark))
        if isinstance(bd, dict) and any(isinstance(v, list) and v and isinstance(v[0], list) for v in bd.values()):
            bench_rets, _ = klines_to_returns(next(iter(bd.values())))
        elif isinstance(bd, list):
            bench_rets = [r["ret"] for r in bd]
        else:
            sys.exit("refused honestly -- benchmark must be a klines JSON or a {date, ret} list")
        relative = relative_metrics(rets, bench_rets, args.periods_per_year)
        if isinstance(relative, dict) and "unavailable" in relative:
            print(f"benchmark-relative unavailable: {relative['unavailable']}")
            relative = None

    print(t("header", label=label) + "\n")
    rows = render_rows(m)
    for k, v in rows:
        print(f"- **{k}**: {v}")
    kind = t("ppy_kind_crypto") if args.periods_per_year == 365 else t("ppy_kind_equity")
    warn = t("noise_warn") if m["periods"] < 30 else ""
    if relative:
        print("\n## benchmark-relative (period-based, disclosed)")
        print(f"- beta: {relative['beta_period_based']:.2f} | alpha(ann, simplified): {relative['alpha_annualized']:+.2%}")
        print(f"- mean excess/period: {relative['mean_excess_period']:+.4%} | total excess: {relative['excess_total']:+.2%}")
        print(f"- caliber: {relative['caliber']}")
    if ledger_note:
        print("\n" + ledger_note)
    print("\n" + t("honesty_title"))
    for line in t("honesty_lines", ppy=args.periods_per_year, kind=kind, n=m["periods"], warn=warn):
        print(f"- {line}")
    print(f"\n---\n*{t('footer', ts=dt.datetime.now().isoformat(timespec='seconds'))}*")

    if args.save:
        global ENVELOPE_PPY
        ENVELOPE_PPY = args.periods_per_year
        dds = m.pop("_dd_series")
        envelope = {"schema": "perf-report/0", "label": label,
                    "honesty": {"annualization_factor": args.periods_per_year,
                                "var_method": "historical non-parametric quantile",
                                "sample_size_warnings": ([f"n={m['periods']} < 30: Sharpe/Sortino noise zone"]
                                                         if m["periods"] < 30 else []),
                                "periods": m["periods"],
                                "caliber": "all trade statistics are period-based, not trade-based"},
                    "source": source,
                    "metrics": {k: v for k, v in m.items() if k != "equity_curve"}}
        jpath = f"reports/{symbol.replace('/', '_')}-{args.strategy}-{dt.date.today()}.json"
        json.dump(envelope, open(jpath, "w"), ensure_ascii=False, indent=1, default=str)
        print(t("saved", path=jpath), file=sys.stderr)
        html = ("<!doctype html><meta charset=utf-8><body style='font-family:monospace;max-width:760px;margin:20px auto'>"
                f"<h3>Tearsheet · {label}</h3>"
                + svg_equity(m["equity_curve"], dates, label)
                + svg_drawdown(dds, dates)
                + "<pre>" + "\n".join(f"{k:>20}: {v}" for k, v in rows) + "</pre>"
                + "<hr><small>annualization=" + str(args.periods_per_year) + " · VaR=historical non-parametric · past ≠ future</small></body>")
        os.makedirs("reports", exist_ok=True)
        path = f"reports/{symbol.replace('/', '_')}-{args.strategy}-{dt.date.today()}.html"
        open(path, "w").write(html)
        print(t("saved", path=path), file=sys.stderr)


if __name__ == "__main__":
    main()
