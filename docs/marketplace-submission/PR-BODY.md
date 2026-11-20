# PR body（提交 awesome-dsh-plugin 用——owner 发布 npm 0.2.0 后执行）

**Adds vicfei/dsh-quantstats — performance tearsheets, honesty included (tools)**

One file added: `data/plugins/vicfei__dsh-quantstats--npm.yml`.

- Install: `dsh plugin add dsh-quantstats` (npm 0.2.0; dsh.bundle + skill +
  CLI spawning the stdlib-only Python engine)
- What it does: performance tearsheets where **every metric rides with its
  caliber** (all trade statistics period-based, disclosed in-band) and the
  honesty trio (annualization factor / VaR method / sample-size alerts) is
  structural in every artifact. Upstream vocabulary (Sharpe/Sortino/Calmar/
  VaR/CVaR/ulcer/tail/payoff/profit factor), inline-SVG tearsheets,
  benchmark-relative mode — plus **the family data plane**: a
  dsh-TradingAgents settled ledger becomes the committee scorecard in one
  command; any {date, ret} series from family engines tears directly.
- Positioning: the zero-dependency complement to upstream quantstats (the
  completed-state library for notebook quants); the README table says so.
- Real working code: 23 hermetic checks + CI green; live smokes on real BTC
  data and the real committee ledger. Concept seat (upstream Apache-2.0, no
  upstream code). Not investment advice. Family: dsh-TradingAgents ·
  dsh-jesse · dsh-Kronos …

PR 执行命令（owner 在 npm 0.2.0 发布后跑）：

```bash
cd /tmp && git clone --depth 1 git@ssh.github.com:vicfei/awesome-dsh-plugin.git && cd awesome-dsh-plugin
git checkout -b add-dsh-quantstats
cp ~/dsh-quantstats/docs/marketplace-submission/vicfei__dsh-quantstats--npm.yml data/plugins/
git add data/plugins/vicfei__dsh-quantstats--npm.yml
git commit -m "Add vicfei/dsh-quantstats (performance tearsheets, honesty included)"
git push -f origin add-dsh-quantstats
# 开 PR：base awesome-dsh-plugin/awesome-dsh-plugin ← vicfei:add-dsh-quantstats，body 用上文
```
