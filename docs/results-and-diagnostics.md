# 结果与诊断口径

## 分数

113道题，各评估3次，共339个trial。原生verifier reward=1计通过，reward=0或缺失计为未通过。汇总统计全部attempt的平均通过率。

## 诊断字段

| 字段 | 统计方式 |
|---|---|
| 截断响应 | `incomplete_details.reason=max_output_tokens`，按response ID去重 |
| 工具超时 | 轨迹中的工具调用超时，按call ID去重 |
| AgentTimeoutError | 整题agent时间预算耗尽 |
| VerifierTimeoutError | verifier时间预算耗尽 |
| RepeatedFormatError | mini-SWE轨迹中的退出状态 |
| 空patch / 缺失patch | 分别统计文件大小为0和文件不存在 |
| 缺失轨迹 / reward | 分别检查轨迹文件及原生verifier结果 |

诊断项可能重叠。逐题数据见 [JSON](../data/latest-results.json) 和 [CSV](../data/trials.csv)。新运行的统计使用 [summarize.py](../scripts/summarize.py)，只读取日志和结果，不重新打分。
