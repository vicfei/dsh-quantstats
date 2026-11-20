#!/usr/bin/env python3
"""Hermetic engine tests — no network, no LLM. Synthetic series only.
Run: python3 tests/test_engine.py   (exits non-zero on any FAIL)"""
import math, random, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tearsheet as ts

FAILS = []


def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        FAILS.append(name)


rng = random.Random(7)
rets = [rng.gauss(0.001, 0.02) for _ in range(300)]

# 1. metrics core + determinism
m1 = ts.metrics(rets, 365, "T")
m2 = ts.metrics(rets, 365, "T")
check("metrics deterministic", m1 == m2)
check("metrics periods", m1["periods"] == 300)

# 2. wordlist sanity
check("payoff positive finite", math.isfinite(m1["payoff_ratio_periods"]) and m1["payoff_ratio_periods"] > 0)
check("profit_factor positive", m1["profit_factor"] > 0)
check("consecutive within bounds", 1 <= m1["consecutive_wins_periods"] <= 300 and 1 <= m1["consecutive_losses_periods"] <= 300)
check("ulcer in [0,1]", 0 <= m1["ulcer_index"] <= 1)
check("tail_ratio positive", m1["tail_ratio"] > 0)

# 3. known-answer: constant positive returns
flat_up = [0.01] * 100
mf = ts.metrics(flat_up, 365, "F")
check("flat-up: no losses → payoff 0 profit_factor 0", mf["payoff_ratio_periods"] == 0.0 and mf["profit_factor"] == 0.0)
check("flat-up: dd zero ulcer zero", mf["max_drawdown"] == 0.0 and mf["ulcer_index"] == 0.0)

# 4. preconditions refuse
probs = ts.check_preconditions([0.01] * 5)
check("short series refused", any("insufficient" in p for p in probs))
probs = ts.check_preconditions([0.01] * 50)
check("zero-variance refused", any("zero-variance" in p for p in probs))

# 5. gap detection
import datetime as dt
bars = []
d = dt.date(2025, 1, 1)
for i in range(60):
    bars.append([d.isoformat(), 1, 1, 1, 1, 1])
    d += dt.timedelta(days=1 if i != 40 else 15)
g = ts.coverage_gaps(bars)
check("15-day gap detected", len(g) == 1 and g[0]["calendar_days"] == 15)

# 6. i18n
for lang in ("en", "zh"):
    ts.LANG = lang
    hdr = ts.t("header", label="T")
    check("header in %s" % lang, "Tearsheet" in hdr or "Tearsheet" in hdr)
    lines = ts.t("honesty_lines", ppy=365, kind="crypto", n=100, warn="")
    check("honesty 4 lines in %s" % lang, len(lines) == 4)
ts.LANG = "en"

# 7. envelope structure (shape of what --save writes)
env_honesty = {"annualization_factor": 365, "var_method": "historical non-parametric quantile",
               "sample_size_warnings": [], "periods": 300,
               "caliber": "all trade statistics are period-based, not trade-based"}
check("envelope keys", set(env_honesty) == {"annualization_factor", "var_method",
                                            "sample_size_warnings", "periods", "caliber"})

# 8. V2: loaders + relative metrics
import json as _json, tempfile as _tf
with _tf.TemporaryDirectory() as td:
    ser = [{"date": f"2026-01-{i+1:02d}", "ret": rng.gauss(0.001, 0.01)} for i in range(30)]
    p = os.path.join(td, "s.json")
    _json.dump(ser, open(p, "w"))
    check("load_series json round-trip", ts.load_series(p) == ser)
    csv_p = os.path.join(td, "s.csv")
    open(csv_p, "w").write("date,ret\n" + "\n".join(f"{r['date']},{r['ret']}" for r in ser[:5]))
    check("load_series csv", len(ts.load_series(csv_p)) == 5)

led = {"entries": [
    {"ticker": "A", "date": "2026-11-01", "decision": "HOLD", "pending": False,
     "settled_return": 0.03, "resolution_date": "2026-11-08", "synthetic": False},
    {"ticker": "B", "date": "2026-11-02", "decision": "PASS", "pending": False,
     "settled_return": None, "synthetic": False},
    {"ticker": "C", "date": "2026-11-03", "decision": "OVERWEIGHT", "pending": True, "synthetic": False},
    {"ticker": "D", "date": "2026-11-04", "decision": "HOLD", "pending": False,
     "settled_return": 0.02, "resolution_date": "2026-11-11", "synthetic": True},
]}
with _tf.TemporaryDirectory() as td:
    lp = os.path.join(td, "ledger.json")
    _json.dump(led, open(lp, "w"))
    rows, stats = ts.load_ledger(lp)
    check("ledger: only scored directed count", stats["scored"] == 1 and rows[0]["ret"] == 0.03)
    check("ledger: pending/synthetic/unscored counted", stats["pending"] == 1
          and stats["synthetic_excluded"] == 1 and stats["resolved_unscored"] == 1)

a = [0.01, 0.02, -0.01, 0.015, 0.005, -0.002, 0.012, 0.008, -0.004, 0.011, 0.006, -0.003]
b = [0.005, 0.01, -0.005, 0.008, 0.002, -0.001, 0.006, 0.004, -0.002, 0.005, 0.003, -0.001]
rel = ts.relative_metrics(a, b, 252)
check("relative: beta ~ 2 for doubled series", 1.5 < rel["beta_period_based"] < 2.5)
check("relative: alpha positive", rel["alpha_annualized"] > 0)
check("relative: unavailable on short", "unavailable" in ts.relative_metrics(a[:5], b[:5], 252))

print("result:", "GREEN" if not FAILS else "RED (%d)" % len(FAILS))
sys.exit(1 if FAILS else 0)
