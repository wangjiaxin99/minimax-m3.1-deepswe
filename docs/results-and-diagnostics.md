# 结果与诊断口径

## 分数

下述历史数据来自三个顺序执行的全量job，每job的attempt=1。新脚本按用户要求改为一个job的`--n-attempts 3`，共339个trial、并发64；仍统计全部attempt的平均通过率，不取每题最佳。调度方式改变，历史轮次耗时不能直接当成新job的分轮耗时。

每题每轮正式 attempt=1，三轮独立全量 job。原生 verifier reward=1 才计通过，reward=0 或无 reward 不通过。三轮总通过数 / 339 等于三轮正确率的算术平均；不用部分测试通过率、`pass@3` 或三轮每题取最佳替代。

`max-retries=2` 是 Pier 对可重试异常的框架策略。本批表格保留最终原生 trial 结果，不对正常已计分失败额外生成答案。增加环境资源或补验 verifier 应另存结果并解释规则，不能覆写该批结果。

## 截断

按唯一 Responses API response ID 去重，同时读取轨迹中的直接 response 与 `extra.response`。判断 `incomplete_details.reason == max_output_tokens`，结合 usage 与实际预算分析原因。

| 格式 | 轮次 / 任务 | 次数 | 实际输出预算 | 最终状态 |
|---|---|---:|---|---|
| MXFP8 | r3 / expr-try-catch-errors | 5 | 17081–17478 | RepeatedFormatError，空 patch，reward 0 |
| MXFP4 | r1 / scriggo-method-declarations | 1 | 12622 | Submitted，有 patch，reward 0 |
| MXFP4 | r3 / opa-rego-rule-profiling | 8 | 90–19039 | RepeatedFormatError，空 patch，reward 0 |

这 14 次响应均在输入+输出=524288 时停止，实际输出小于请求的65536。扩大输出上限无法自动解决历史消息填满上下文；mini-SWE 当前运行没有 Codex 同样的自动压缩行为。发生截断的题目均失败，仍不能证明它是每个失败的唯一原因。

## 超时和 OOM

- 30 秒工具命令超时：只统计 `function_call_output.extra.exception_info` 明确的超时，按 call ID 去重。agent 收到工具错误后可继续，很多任务最终通过。
- 整题超时：Pier 顶层 `AgentTimeoutError`。MXFP8 r1 的 kcp-go；r3 的 kcp-go、textual。
- verifier 超时：MXFP8 r3 与 MXFP4 r1 的 `pwntools-tube-multiplexing`；均没有 reward，保留在分母，没有补验。
- CPU OOM：两种格式的 `kea-atomic-signal-selectors` 三轮均由任务容器 OOM 杀掉 mini-SWE，最终失败。结合历史内核证据确认；不要仅看 exit137。
- 其他构建/测试子进程也曾 OOM，agent 可能恢复；OOM 内核事件数与失败题数不同。MXFP8 r2/r3 留存 23/24 次事件（各涉及5个题目轮次）；同口径结构化监控未覆盖r1。MXFP4 r1/r2/r3 为22/24/24次，共70次，涉及14个题目轮次，其中10个最终通过。

诊断项会重叠，不能相加作为失败总数。正式678个trial均保留轨迹和patch文件，但存在空patch。顶层exception未发现环境构建或agent安装失败类型，不代表过程中每个工具命令都成功。

## 公开数据与原始日志

[latest-results.json](../data/latest-results.json) 和 [trials.csv](../data/trials.csv) 来自历史只读审计的白名单字段。每题包含原生 `result.json` 的 SHA256、reward、退出/异常类型、截断、工具超时及 token 上限统计。它们可用于核对本表的计数，完整模型输出和失败测试细节仍需原始轨迹及 verifier 日志。

仓库没有附上完整轨迹、测试代码或模型答案。公开数据用于复核统计结果；新实验应保存自己的完整轨迹和verifier日志，并遵守任务及代码许可证。`scripts/summarize.py` 是便于新实验使用的通用只读统计工具；已发布数据以完成的历史审计导出为准。
