# 评估配置与数据

## 已有结果使用的模型

- Baseline：[Quark MXFP8](https://huggingface.co/amd/MiniMax-M3.1-Flash-Quark-MXFP8)。
- 对比模型：[Quark MXFP4](https://huggingface.co/amd/MiniMax-M3.1-Flash-Quark-MXFP4)。

运行时通过 `.env` 的 `MODEL_PATH` 指定要评估的checkpoint。以上是已有结果的模型来源；每次运行评估一个指定模型，没有baseline前置要求或模型评估顺序。

## 配置

Pier 0.3.1 + mini-SWE-agent 2.4.5；TP4；上下文524288；输出65536；并发64；每题3次attempt；max-retries=2；reasoning_effort=max；temperature=1；top_p=0.95；NVFP4 KV/indexer cache。

参数逐项来源见 [README配置表](../README.md#5-单个-job-全量运行三次-attempt)及 [参数参考来源](references.md)。mini-SWE-agent 2.4.5和512K上下文来自MiniMax官方模型卡；temperature/top_p来自其通用建议。DeepSWE官方v1.1排行榜采用4次完整运行、计划452次；本仓库当前采用3次、共339次，其余本次服务和预算设置均在来源表中单独标明。

## 数据

- [最新结果JSON](../data/latest-results.json)：每个模型、每轮得分、耗时和逐题诊断。
- [678个题目轮次CSV](../data/trials.csv)：reward、agent状态、异常、截断、工具超时和token统计。
- [版本指纹](../data/versions.json)：镜像digest、源码commit和补丁SHA256。
- [数据校验脚本](../scripts/check_published_data.py)：核对题数、分数和诊断计数。

按原生reward=1统计通过，固定339分母。公开数据不包含模型权重、完整生成轨迹或任务解法。
