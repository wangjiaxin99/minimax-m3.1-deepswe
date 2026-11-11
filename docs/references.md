# 参数参考来源

下列来源区分“官方评估说明”“框架参数语义”和“本仓库实验设置”。框架支持某个参数，不代表官方评估采用本仓库的取值。

## S1

**DeepSWE官方：Pier + mini-SWE、113题及任务预算。**

- [固定版本README：Quickstart与What is Pier](https://github.com/datacurve-ai/deep-swe/blob/0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea/README.md#quickstart)：运行示例使用 `pier run --agent mini-swe-agent`；正文说明排行榜使用Pier + mini-SWE-agent，在Modal上运行。v1.1的独立verifier要求Pier > 0.3.0。
- [固定版本task.toml示例](https://github.com/datacurve-ai/deep-swe/blob/0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea/tasks/task-task-graph-export/task.toml)：agent预算10800秒、verifier预算1800秒、环境构建预算1800秒。该快照的113题均采用这些预算。
- [Harbor独立verifier格式](https://www.harborframework.com/docs/tasks#verifier-environment-shared-vs-separate)：任务与独立verifier环境的接口。

本仓库固定Pier 0.3.1并使用Docker沙箱；Docker部署、并发64不是上述官方README要求。

## S2

**MiniMax官方模型卡：agent版本、上下文和采样建议。**

[MiniMax-M3.1-Flash模型卡，固定revision](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash/blob/2f33a8b9ae49ce7b51c994df97166a7fd059bc2e/README.md)：

- Evaluation Notes明确写明DeepSWE v1.1使用mini-SWE-agent 2.4.5、512K context。
- Usage建议 `temperature=1.0`、`top_p=0.95`，是通用采样建议。
- 列出可用 `reasoning_effort` 档位，包括 `max`；没有注明DeepSWE成绩具体采用哪个档位。

模型卡未披露DeepSWE重复次数、并发、TP、KV量化、单响应输出上限及完整服务命令。本仓库将512K配置为524288 token，将输出配置为65536 token、effort配置为max；后两项是实验设置，不能据此声称完整复现官方分数。

## S3

**三次重复与两次重试：实验设置及公开示例。**

[NVIDIA Switchyard DeepSWE qualification，固定commit](https://github.com/NVIDIA-NeMo/Switchyard/blob/365ce830bfa8a1358bb2aa944703233e762d7a52/benchmark/DEEPSWE_V11_QUALIFICATION.md)中，Advisor和Plan/execute分别采用3次独立运行、报告均值与样本标准差，并设置Infrastructure retries=2。该实验使用Codex CLI 0.154.0，其agent、模型路由和服务配置与本仓库不同。

本仓库采用 `--n-attempts 3`，用于观察重复运行波动并统计平均通过率；`--max-retries 2`用于可重试异常。上述NVIDIA实验是相同取值的公开参考，不能证明本仓库历史取值最初来自它，也不是DeepSWE或MiniMax要求。

**DeepSWE官方v1.1排行榜采用四次完整运行。** [官方排行榜JSON](https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json)在本次核对的快照中（`generated_at=2026-09-22`），记录 `n_runs=4`，完整计划量为113×4=452次。对齐该轮数应使用 `--n-attempts 4`；本仓库已有结果和当前脚本采用3次、共339次。

[官方运行说明](https://deepswe.datacurve.ai/run)及固定版本README未把4次写成所有本地评估的强制要求；这里区分排行榜的四次设置与本仓库的三次设置。未查到AA针对DeepSWE必须3次的公开规定。

三次attempt的平均通过率按全部339次统计，不能按“任意一次成功”统计为pass@3。正式attempt和框架异常重试是不同参数。

## S4

**Pier参数定义与默认值，固定commit。**

- [CLI参数](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/cli/jobs.py)：`--n-attempts`、`--n-concurrent`、`--max-retries`、超时倍率、`--ak`、`--ae`、`--delete/--no-delete`。
- [JobConfig / RetryConfig](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/models/job/config.py)：默认attempt=1、并发=4、max_retries=0；本仓库显式覆盖为3、64、2。
- [mini-SWE接入](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/agents/installed/mini_swe_agent.py)：版本安装、额外Python包、模型参数传递；接入层默认cost_limit=0，`openai/`模型自动选择 `litellm_response`。
- [Trial setup默认预算](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/trial/trial.py)及[超时计算](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/trial/execution.py)：agent setup默认360秒，本仓库倍率5得到1800秒；它与题目的environment build预算是不同阶段。
- [Docker清理实现](https://github.com/datacurve-ai/pier/blob/b26211ed2bbee6d145f6b8c5b80e39f18b296f08/src/pier/environments/docker/docker.py)：`--no-delete`使用Compose down，移除普通任务容器/网络并保留镜像及卷；`--delete`还请求删除镜像和卷。

## S5

**mini-SWE-agent 2.4.5参数语义。**

- [Responses客户端源码](https://github.com/SWE-agent/mini-swe-agent/blob/v2.4.5/src/minisweagent/models/litellm_response_model.py)：经LiteLLM发送Responses请求，并传递 `model_kwargs`。
- [Agent限制源码](https://github.com/SWE-agent/mini-swe-agent/blob/v2.4.5/src/minisweagent/agents/default.py)：cost_limit大于0才启用费用限制；包本身默认3.0，Pier接入覆盖为0。
- [本地命令环境源码](https://github.com/SWE-agent/mini-swe-agent/blob/v2.4.5/src/minisweagent/environments/local.py)：工具命令默认timeout=30秒；本仓库未覆盖这个默认值。
- [LiteLLM参数丢弃说明](https://docs.litellm.ai/docs/completion/drop_params)：`drop_params=False`不静默丢弃不受支持的参数。本仓库显式传递该值，防止请求参数被忽略。

LiteLLM 1.108.3、MCP 2.3.0是本仓库固定的agent依赖版本，没有查到官方DeepSWE要求这两个版本。

## S6

**vLLM参数接口与MXFP8支持。**

- [vLLM serve参数文档](https://docs.vllm.ai/en/latest/cli/serve/)：TP、max-model-len、KV cache及其他服务参数的语义。
- [工具调用文档](https://docs.vllm.ai/en/latest/features/tool_calling/)及[reasoning文档](https://docs.vllm.ai/en/latest/features/reasoning_outputs/)：解析器和自动工具调用接口。
- [vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125)：001补丁的Quark MXFP8 MoE权重加载和AITER推理支持。

在线vLLM文档可能随版本更新；实际实现由本仓库的基础镜像digest与补丁固定。TP4、NVFP4 KV/indexer cache、AITER、block size128及其他服务开关是本次ROCm部署配置，不是DeepSWE官方评估要求。完整参数见 [server.sh](../scripts/server.sh)，指纹见 [versions.json](../data/versions.json)。
