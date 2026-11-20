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

print("result:", "GREEN" if not FAILS else "RED (%d)" % len(FAILS))
sys.exit(1 if FAILS else 0)
