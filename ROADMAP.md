# ROADMAP — dsh-quantstats

北极星：九仓家族的绩效报告层，吃 QuantStats 7.9k★ 流量，30 天 100–300★。
命名全表面：GitHub=npm=dsh-quantstats（镜像上游小写仓名）。
家族分工：nautilus=回测 / jesse=调参 / **本仓=测量与报告**——所有引擎的产出
都该流经这里出一张诚实的成绩单。

## 里程碑

### M0 ✅（2026-11-17）
tearsheet 引擎（夏普/索提诺/卡尔玛/回撤/VaR/CVaR/偏度/胜率 + 零依赖 SVG
权益与回撤曲线 + 诚实件三则：年化因子披露/历史 VaR 声明/样本量警报）。
真实冒烟：BTC 365d 熊年双表（持有 -29.9%/回撤 -39.5% vs SMA20/60 +1.6%/-19.3%）。

### M0.5 · 发布包
- [ ] README 打磨 + 双表对比截图 + npm 0.0.1 占位（owner 手动）
- [ ] 公开仓 topics + 九仓互链 + marketplace + 渠道

### M1 · 深度（第 2-3 周）
- [ ] 滚动指标（rolling Sharpe/DD 曲线）+ 基准相对模式（超额/alpha/beta）
- [ ] 直接消费家族引擎产出（nautilus/jesse/hummingbot 的收益序列 → tearsheet）

### M2 · 插件化（第 4-6 周）
- [ ] cordis 插件 typed tools（tearsheet.run / metrics.compute）

### M3 · 生态（第 2 月起）
- [ ] 报告标准（PERF-REPORT spec，与 IC-MEMO/OPT-REPORT/RESEARCH-TRAIL 会师成家族四格式）

## 纪律（不可让步）

- 诚实件（年化因子/VaR 方法/样本量警报）不可从任何输出剥离；
- 指标为描述统计，不得作预测表述；不做投资建议。
