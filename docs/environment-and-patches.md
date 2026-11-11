# 环境与补丁

## 固定版本

完整记录见 [versions.json](../data/versions.json)。

| 组件 | 版本 / 固定方式 |
|---|---|
| vLLM / PyTorch / Triton / AITER | 固定ROCm基础镜像digest，再应用001补丁 |
| vLLM | `0.32.0rc1.dev364+g8d0f05a0c.d20261023.rocm100` |
| PyTorch / Triton | `2.13.0+rocm10.0.0` / `3.8.0+git669b31ac` |
| Pier | 0.3.1，`b26211ed2bbee6d145f6b8c5b80e39f18b296f08` |
| DeepSWE | `0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea`，113题 |
| mini-SWE-agent | 2.4.5 |
| agent LiteLLM / MCP | 1.108.3 / 2.3.0 |
| Pier依赖 | vLLM镜像内的独立 `/opt/pier-venv`，使用上游固定commit的 `uv.lock` |
| Docker / Compose / UV | 28.3.2 / 2.38.2 / 0.13.5 |

AITER随vLLM基础镜像固定。使用相同镜像digest，无需单独安装或指定AITER commit。

```text
vllm/vllm-openai-rocm@sha256:ae8681212aa5291d8c27f06e90016435e3fca144a68fd5c439231f6475f74569
```

## 补丁顺序

补丁按本仓库顺序编号，由Dockerfile自动应用。

### 001：MXFP8模型加载与推理

[001-vllm-quark-mxfp8.patch](../patches/001-vllm-quark-mxfp8.patch)来自[vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125)。增加 `QuarkW8A8Mxfp8MoEMethod`，支持MXFP8专家权重及scale加载，并接入AITER MXFP8 MoE推理路径。MXFP4使用已有的 `QuarkOCP_MX_MoEMethod`。

Dockerfile应用 `quark_moe.py` 的运行时改动，并校验源码SHA256：

| 状态 | SHA256 |
|---|---|
| 应用前 | `3a3179009acd47f896b12fd805c08986bea538764a584db918582fdcc5a914d1` |
| 应用后 | `3f3397675af6596964daf974ee3b22d10996d0ebc70a4c3b30cad0e78f8ac830` |

### 002：Pier子网与模型服务配置

[002-pier-provider-subnets.patch](../patches/002-pier-provider-subnets.patch)为每个trial分配两个独立 `/29` 子网，通过文件锁保证并发分配唯一性；同时支持Codex显式模型服务地址的白名单配置。

### 003：Pier mini-SWE模型服务白名单

[003-pier-mini-provider-allowlist.patch](../patches/003-pier-mini-provider-allowlist.patch)让Pier的mini-SWE接入按显式模型API地址生成白名单。

002/003修改Pier的基础设施接入代码，不修改mini-SWE解题逻辑、任务或verifier。

## 部署

`Dockerfile.vllm`同时安装vLLM和Pier。模型服务使用原有Python环境；评估脚本激活 `/opt/pier-venv`。`Dockerfile.sandbox`提供独立Docker daemon，任务镜像、构建缓存及容器数据持久化到 `SANDBOX_DATA_DIR`。

## 沙箱配置

独立Docker daemon启用init、持久化镜像缓存、模型HTTP转发和DNS转发。配置位于 [compose.yaml](../compose.yaml) 和 [sandbox-entrypoint.sh](../docker/sandbox-entrypoint.sh)。

## 镜像迁移

使用digest拉取基础镜像，也可将同一镜像导出到目标机器：

```bash
docker pull vllm/vllm-openai-rocm@sha256:ae8681212aa5291d8c27f06e90016435e3fca144a68fd5c439231f6475f74569
docker save vllm/vllm-openai-rocm@sha256:ae8681212aa5291d8c27f06e90016435e3fca144a68fd5c439231f6475f74569 -o minimax-vllm-base.tar
docker load -i minimax-vllm-base.tar
```
