# dsh-quantstats — DeepSeek Harness 的绩效 tearsheet，自带诚实件

**夏普/索提诺/卡尔玛/回撤/VaR——从收益序列确定性计算，零依赖 SVG tearsheet
呈现，假设显式披露、样本量警报常开。会声明自身边界的报告。**

[English](README.md) | [简体中文](README.zh-CN.md)

## 上游 quantstats 的位置（互补，不是对手）

上游 [quantstats](https://github.com/ranaroussi/quantstats)（7.9k★，yfinance
作者出品）是完成态 Python 库：~60 指标、20 种图、HTML tearsheet、重栈
（pandas/scipy/matplotlib/seaborn/yfinance）。**在 pandas notebook 里，用
quantstats。** dsh-quantstats 是 **DSH 会话报告层**：零依赖、每个指标自带
口径（period-based，随行披露）、内联 SVG tearsheet、家族工件消费。

| | 上游 quantstats（互补） | **dsh-quantstats** |
|---|---|---|
| 形态 | notebook 的 Python 库 | **DSH 插件**——agent 问，报告出 |
| 依赖 | pandas/scipy/matplotlib/seaborn/yfinance | **零（纯标准库）** |
| 口径 | README 里的 period-vs-trade 披露 | **每个指标带口径行，随数字输出** |
| 数据 | yfinance 下载 | **你的序列 / 家族工件** |

## 快速开始

```bash
python3 scripts/tearsheet.py --data <klines.json>                      # 买入持有
python3 scripts/tearsheet.py --data klines.json --strategy sma --save  # SMA 策略
python3 scripts/tearsheet.py --data klines.json --lang zh              # 中文回退
```

## 许可与免责

MIT 概念位（上游 Apache-2.0，零上游代码）。**指标为描述统计，非预测；
非投资建议。**
