<p align="center"><img src="https://capsule-render.vercel.app/api?type=waving&color=0:6A5ACD,100:2E86C1&height=180&section=header&text=alpha4j&fontSize=46&fontColor=ffffff&animation=fadeIn&desc=Qlib%20%2F%20WorldQuant%20Alpha%20factors%20for%20JDK%2017%2B&descAlignY=68" alt="alpha4j banner" /></p>
<p align="center"><a href="https://github.com/whaleal-dev/alpha4j"><img src="https://img.shields.io/badge/GitHub-whaleal--dev%2Falpha4j-181717" alt="GitHub" /></a> <a href="https://whaleal.com"><img src="https://img.shields.io/badge/Docs-whaleal.com-0A7EA4" alt="Docs" /></a> <a href="https://www.apache.org/licenses/LICENSE-2.0.txt"><img src="https://img.shields.io/badge/License-Apache%202.0-1F6FEB" alt="License" /></a> <img src="https://img.shields.io/badge/JDK-17%2B-2EA043" alt="JDK 17+" /></p>

# alpha4j

**alpha4j 是面向 JDK 17+ 的 Java Alpha 因子库**，不是交易平台、不是技术分析引擎、也不是现成的选股软件。

它只做一件事：把 K 线算成固定维度的因子向量，给你的模型或打分逻辑当选股特征。纯 Java，无 Python 依赖。

- 版本：`1.0.0`
- 坐标：`com.whaleal.quant:alpha4j`
- GitHub：[whaleal-dev/alpha4j](https://github.com/whaleal-dev/alpha4j)
- 维护者：恒哥

## 项目范围

### 范围内（本仓库提供）

| 能力 | 说明 |
|------|------|
| Alpha101 | WorldQuant 因子；当前 **80 / 101**（缺行业中性化 / 未公开公式项） |
| Alpha158 | Qlib 标准 **159** 维（含 VOLUME0）；排除算子占位，维度固定 |
| Alpha360 | Qlib **360** 维（60 日 × 6 字段；窗口目前硬编码） |
| 特征输出 | `AlphaFactorResult` / `AlphaDataset`，训练与推理同序 |
| 增量计算 | Alpha158 `calculateIncremental` |
| K 线模型 | 自带 `Candlestick`（`double` 价格字段） |

### 范围外（不提供，请在业务侧自行实现）

- 行情接入、券商下单、持仓与对账
- 组合回测、调仓、风控（那是 quant-platform `sdk/` / [ta4j](https://github.com/ta4j/ta4j) 的事）
- 选股模型训练、排序阈值、实盘信号
- Python Qlib 运行时、行业中性化（IndNeutralize）横截面数据

一句话：**库把 K 线变成因子向量；不负责拉行情，也不负责决定买哪只。**

## 安装

尚未发布 Maven Central。本地安装：

```bash
git clone git@github.com:whaleal-dev/alpha4j.git
cd alpha4j
mvn -DskipTests install
```

- Gradle：`implementation 'com.whaleal.quant:alpha4j:1.0.0'`
- Maven：`<dependency><groupId>com.whaleal.quant</groupId><artifactId>alpha4j</artifactId><version>1.0.0</version></dependency>`

## 30 秒跑通

K 线按时间升序。Alpha158 至少 60 根；Alpha101 建议 250 根（少于 60 根会失败）。

```java
import com.whaleal.quant.alpha4j.Alpha158Config;
import com.whaleal.quant.alpha4j.AlphaFactorResult;
import com.whaleal.quant.alpha4j.calculator.Alpha101Calculator;
import com.whaleal.quant.alpha4j.calculator.Alpha158Calculator;
import com.whaleal.quant.alpha4j.calculator.Alpha360Calculator;
import com.whaleal.quant.alpha4j.model.Candlestick;

import java.util.List;

public class Alpha4jFirstRun {
    public static void main(String[] args) {
        List<Candlestick> bars = loadKLineData();

        AlphaFactorResult a158 = Alpha158Calculator.calculate(bars);
        System.out.println(a158.getFactorCount()); // 159
        System.out.println(a158.getFactors().get("ROC5"));

        AlphaFactorResult a360 = Alpha360Calculator.calculate(bars);
        AlphaFactorResult a101 = new Alpha101Calculator().calculate(bars);
    }
}
```

扩展 179 维（前 159 个与标准配置同序）：

```java
AlphaFactorResult extra = Alpha158Calculator.calculate(bars, Alpha158Config.createExtended());
```

## 因子集补充

Alpha158 默认：K 线形态 9 + 价格 4 + VOLUME0 + 滚动统计 145 = 159。

| 集合 | 来源 | 维数 |
|------|------|------|
| Alpha101 | WorldQuant | 实现 80 / 101 |
| Alpha158 | Qlib | 159（`createExtended()` → 179） |
| Alpha360 | Qlib | 360 |

## 已知限制

- Alpha101 未覆盖需要横截面行业中性化的因子。
- `Alpha360Config` 的窗口 / 字段开关目前未生效。
- 不含行情与组合回测。

组织：[whaleal-dev](https://github.com/whaleal-dev) · 官网：[whaleal.com](https://whaleal.com)

<!-- [恒哥] -->
