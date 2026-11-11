# 参考来源及适用范围

## 官方框架与任务

- [DeepSWE 仓库](https://github.com/datacurve-ai/deep-swe)，本实验固定 [0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea](https://github.com/datacurve-ai/deep-swe/tree/0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea)。README Quickstart 使用 `pier run ... --agent mini-swe-agent`，说明排行榜使用 Pier + mini-SWE 在 Modal 运行。v1.1 的独立 verifier 要求 Pier 高于0.3.0。
- [Pier 仓库](https://github.com/datacurve-ai/pier)，固定 [b26211ed2bbee6d145f6b8c5b80e39f18b296f08](https://github.com/datacurve-ai/pier/tree/b26211ed2bbee6d145f6b8c5b80e39f18b296f08)。包名 `datacurve-pier`，版本0.3.1。它从Harbor派生，兼容其任务格式并提供agent网络白名单。
- [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)，本实验2.4.5。Pier负责安装、任务生命周期及轨迹收集；mini-SWE负责多轮解题。
- [Harbor任务格式与独立verifier](https://www.harborframework.com/docs/tasks#verifier-environment-shared-vs-separate)，用作格式说明，不等同于本次调度框架或安装版本。
- [vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125)，004补丁的MXFP8 MoE来源。

## 参数来源

选择 Pier + mini-SWE 来自 DeepSWE 官方示例；模型服务的 MiniMax parser、MXFP8适配和AITER配置来自已验证的本地vLLM部署。其余实验条件需要区分来源：

| 条件 | 来源 |
|---|---|
| 113题、agent/verifier预算及资源、独立verifier | 固定版本任务中的 `task.toml` |
| mini-SWE2.4.5、LiteLLM/MCP固定版本 | 本地已运行配置 |
| 并发64、TP4、512K、64K输出、reasoning max | 本次实验设定及历史可用配置，不是DeepSWE统一强制参数 |
| T1 / top_p0.95 | 沿用本地模型生成及评估设置 |
| setup multiplier5、max-retries2 | 本地运行配置；未发现官方要求固定为这两个值 |
| 三个全量独立job | 用户要求连续三轮；不是pass@3或官方三轮强制规范 |
| 036/037网络适配 | 本地模型URL和Docker子网需求 |

官方README中的模型示例没有完整指定每个模型的输出上限，不能由“没写max_output_tokens”推断官方一定使用16K。当前脚本显式65536；上下文由服务显式524288限制，不能把模型标称1M当成本次实际服务长度。

此前查到的公开DeepSWE排行榜配置包含四次运行的设置；不同服务的异常过滤口径也可能与固定339分母不同。本仓库不把这些信息转述成MiniMax官方的同配置结果。若对齐某个排行榜，应另外锁定该模型的agent、prompt、输出/上下文、资源、轮数及异常处理规则。
