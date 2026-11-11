# 环境与补丁

## 固定版本

完整机器可读记录见 [versions.json](../data/versions.json)。

| 组件 | 历史版本 / commit |
|---|---|
| Pier | 0.3.1，`b26211ed2bbee6d145f6b8c5b80e39f18b296f08` |
| DeepSWE | `0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea`，113 题 |
| mini-SWE-agent | 2.4.5，安装到每题 agent 环境 |
| agent LiteLLM / MCP | 1.108.3 / 2.3.0 |
| Pier 控制器依赖 | 固定 Pier commit 的 `uv.lock`，含 Harbor 0.5.0；不把 agent 包版本强装入控制器 |
| vLLM | `0.32.0rc1.dev364+g8d0f05a0c.d20261023.rocm100` + 004 的运行时回移 |
| PyTorch | `2.13.0+rocm10.0.0` |
| Triton | `3.8.0+git669b31ac` |
| UV | 0.13.5 |
| Docker / Compose | 当前复现控制镜像固定 28.3.2 / 2.38.2 |

AITER 位于历史镜像的 `/usr/local/lib/python3.12/dist-packages/aiter/`，没有可读取的 distribution 版本元数据，因此通过基础镜像 digest 固定；不能凭空填一个 AITER commit。PyPI agent 依赖的传递依赖由安装器解析，历史未留下一份完整的跨平台 agent lock；当前固定顶层版本并保留原生安装轨迹，不宣称所有间接依赖及系统包字节相同。

## 004：为了加载并推理 MXFP8 模型

来源：[vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125)。PR head `dfd9547958a186c05c319f7a808f9f91258f76ad`，merge `b6031d71beb219b9c2cbf580745c7307bf15ec91`。

新增 `QuarkW8A8Mxfp8MoEMethod`。专家权重为 FP8E4M3，scale 是以 uint8 存储的 E8M0，每 1×32 元素一组；配置分派、TP 权重/scale 形状、内核布局和动态 MXFP8 activation 接入原生 MXFP8 MoE 后端。MXFP4 继续走 `QuarkOCP_MX_MoEMethod`。

归档 patch 含上游测试改动，当前 Dockerfile **仅应用 `quark_moe.py` 的运行时 hunk**，与历史做法一致。应用前 SHA256：

```text
3a3179009acd47f896b12fd805c08986bea538764a584db918582fdcc5a914d1
```

应用后 SHA256：

```text
3f3397675af6596964daf974ee3b22d10996d0ebc70a4c3b30cad0e78f8ac830
```

未知源码 hash 会构建失败；已是目标 hash 则直接确认。不要再叠加历史 002，也不要将完整 PR 的 merge SHA 当成我们 vLLM wheel 的版本。

## 036 / 037：Pier 本地模型网络适配

新部署额外在sandbox入口配置DNS转发：转发外层容器可用的nameserver，供嵌套Docker准备阶段解析下载地址。避免Docker丢弃外层127.0.0.11后回退到不可达公共DNS；这是Compose基础设施配置，不是新增Pier源码patch。

036 修改 `src/pier/environments/agent_setup.py`：从 `PIER_DOCKER_SUBNET_POOL` 为每个 trial 分配两个独立 `/29`，用 `fcntl.flock` 锁定 `PIER_DOCKER_SUBNET_STATE`，避免并发分配重叠。地址状态不可在存在活跃任务网络时重置。

036 同时调整 Pier 的 Codex 接入白名单；037 对 Pier 的 mini-SWE 接入做相同调整：存在显式模型 URL 时，不额外添加默认公共 provider 域名。这是 Pier 适配代码，不是 mini-SWE-agent 包的解题逻辑修改。

子网和端口适配不会修改 prompt、测试或评分，但网络配置会影响任务能否调用本地模型，所以也是必须记录的环境条件。题目运行时的网络限制与准备阶段的网络下载是两个阶段。网络策略来自题目配置和 Pier 实现；这份仓库未对每条历史网络访问做完整事后审计。

## 基础镜像保留与迁移

历史镜像 tag：`vllm/vllm-openai-rocm:minimax-m31-flash`。

```text
Repo digest:
vllm/vllm-openai-rocm@sha256:ae8681212aa5291d8c27f06e90016435e3fca144a68fd5c439231f6475f74569
Local image ID:
sha256:1d3dac5bca7b1b80983ec0bf4675d1b9feff74a1d683838ade67d06d35c26877
```

digest 是否长期可拉取取决于上游仓库。保留本机原镜像可用：

```bash
docker image inspect vllm/vllm-openai-rocm:minimax-m31-flash
docker save vllm/vllm-openai-rocm:minimax-m31-flash -o /large/disk/minimax-vllm-base.tar
sha256sum /large/disk/minimax-vllm-base.tar
# 在目标机器
docker load -i /large/disk/minimax-vllm-base.tar
```

如果导入镜像没有 RepoDigest，可在 `.env` 使用导入后的 tag，但先核对 image ID 与上述值一致。使用其他镜像、更高版本的 vLLM 或不同 AITER 需要作为新环境记录和验证，不能保证既有补丁 hash 仍适用。

基础 Python、Docker、UV 镜像固定版本；构建验证后进一步记录其 resolved digest。`apt/apk` 仓库和 agent 安装下载不是历史快照，Dockerfile 能重建组件配置，完整字节级复现还需要保存最终镜像和包缓存。
