#!/usr/bin/env python3
"""绩效 tearsheet（quantstats 核心概念的原生实现，M0）

上游 QuantStats（7.9k★，Apache-2.0，yfinance 作者出品）= 量化组合分析：
全套绩效指标 + HTML tearsheet。本插件原生实现该层，差异=家族诚实件：
- 年化因子假设显式披露（crypto 365 / 股票 252，参数化）
- 样本量不足时对 Sharpe/Sortino 打警告（n<30 是噪声区）
- VaR 声明为历史非参数法；"过去业绩≠未来"写进输出
- 零依赖内联 SVG tearsheet（无 CDN，离线可分享）

用法：
  python3 scripts/tearsheet.py --data /tmp/btc_365.json                 # 买入持有
  python3 scripts/tearsheet.py --data /tmp/btc_365.json --strategy sma --fast 20 --slow 60 --save
"""
import argparse, datetime as dt, json, math, sys


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
    for e in eq:
        peak = max(peak, e); mdd = min(mdd, e / peak - 1)
    srt = sorted(rets)
    var5 = srt[max(0, int(0.05 * n) - 1)]
    cvar5 = sum(srt[: max(1, int(0.05 * n))]) / max(1, int(0.05 * n))
    skew = (n / ((n - 1) * (n - 2)) * sum(((r - mean) / std) ** 3 for r in rets)) if n > 2 and std > 0 else 0.0
    return {"label": label, "periods": n, "total_return": total - 1, "cagr": cagr,
            "vol_annualized": std * math.sqrt(periods_per_year),
            "sharpe": mean / std * math.sqrt(periods_per_year) if std > 0 else 0.0,
            "sortino": mean / dstd * math.sqrt(periods_per_year) if dstd > 0 else 0.0,
            "calmar": cagr / abs(mdd) if mdd < 0 else 0.0,
            "max_drawdown": mdd, "var5_hist": var5, "cvar5_hist": cvar5,
            "win_rate_periods": sum(1 for r in rets if r > 0) / n,
            "skew": skew, "best_period": max(rets), "worst_period": min(rets),
            "equity_curve": eq}


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
            f'<text x="10" y="{h-6}" font-size="10" fill="#567">{dates[0]} → {dates[-1]} · {n} periods · dashed=running peak</text></svg>')


def svg_drawdown(eq, dates, w=720, h=140):
    n = len(eq); peak, dds = eq[0], []
    for v in eq:
        peak = max(peak, v); dds.append(v / peak - 1)
    lo = min(dds)
    X = lambda i: 40 + i * (w - 60) / (n - 1)
    Y = lambda v: 16 + v / (lo + 1e-9) * (h - 46)  # v∈[lo,0] → [h-30,16]
    path = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(dds))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="monospace">'
            f'<text x="10" y="12" font-size="12">Drawdown · max {lo:.1%}</text>'
            f'<polyline points="{path}" fill="none" stroke="#c23531" stroke-width="1.2"/>'
            f'<line x1="40" y1="16" x2="{w-20}" y2="16" stroke="#ccc"/>'
            f'<text x="10" y="{h-6}" font-size="10" fill="#567">{dates[0]} → {dates[-1]}</text></svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--strategy", choices=("buyhold", "sma"), default="buyhold")
    ap.add_argument("--fast", type=int, default=20)
    ap.add_argument("--slow", type=int, default=60)
    ap.add_argument("--fee_bps", type=float, default=5)
    ap.add_argument("--periods_per_year", type=int, default=365, help="crypto=365 股票=252（披露用）")
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    data = json.load(open(args.data))
    symbol, bars = next(iter(data.items()))
    if args.strategy == "sma":
        rets, dated = strategy_returns(bars, args.fast, args.slow, args.fee_bps)
        label = f"{symbol} SMA{args.fast}/{args.slow} (fee {args.fee_bps}bps)"
    else:
        rets, dated = klines_to_returns(bars)
        label = f"{symbol} buy&hold"
    m = metrics(rets, args.periods_per_year, label)
    dates = [b[0] for b in dated]

    print(f"## Tearsheet · {label}\n")
    rows = [("periods", m["periods"]), ("total_return", f"{m['total_return']:+.2%}"),
            ("CAGR", f"{m['cagr']:+.2%}"), ("vol(ann)", f"{m['vol_annualized']:.2%}"),
            ("sharpe", f"{m['sharpe']:.2f}"), ("sortino", f"{m['sortino']:.2f}"),
            ("calmar", f"{m['calmar']:.2f}"), ("max_drawdown", f"{m['max_drawdown']:.1%}"),
            ("VaR5(hist)", f"{m['var5_hist']:.2%}"), ("CVaR5(hist)", f"{m['cvar5_hist']:.2%}"),
            ("win_rate(periods)", f"{m['win_rate_periods']:.1%}"), ("skew", f"{m['skew']:.2f}"),
            ("best/worst period", f"{m['best_period']:+.2%} / {m['worst_period']:+.2%}")]
    for k, v in rows:
        print(f"- **{k}**: {v}")
    print(f"""
## 诚实件（假设与警告，不可剥离）
- 年化因子 = {args.periods_per_year}（{"crypto 日频" if args.periods_per_year == 365 else "股票日频"}，参数化假设，换频率须换因子）
- VaR/CVaR 为历史非参数分位数，不含尾部分布假设
- 样本量 {m['periods']}{" ⚠ <30：Sharpe/Sortino 处于噪声区，不可用于比较" if m['periods'] < 30 else ""}
- 过去业绩≠未来表现；本表为描述统计，非预测
---
*engine: tearsheet v0 · 零依赖 SVG · {dt.datetime.now().isoformat(timespec='seconds')} · 非投资建议*""")

    if args.save:
        html = ("<!doctype html><meta charset=utf-8><body style='font-family:monospace;max-width:760px;margin:20px auto'>"
                f"<h3>Tearsheet · {label}</h3>"
                + svg_equity(m["equity_curve"], dates, label)
                + svg_drawdown(m["equity_curve"], dates)
                + "<pre>" + "\n".join(f"{k:>20}: {v}" for k, v in rows) + "</pre>"
                + "<hr><small>annualization=" + str(args.periods_per_year) + " · VaR=historical non-parametric · past ≠ future</small></body>")
        import os
        os.makedirs("reports", exist_ok=True)
        path = f"reports/{symbol.replace('/', '_')}-{args.strategy}-{dt.date.today()}.html"
        open(path, "w").write(html)
        print(f"→ {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
