# 历史实验配置与数据来源

本文记录已完成实验的配置、调度方式和数据口径。仓库不依赖作者机器上的路径、容器或日志目录。

## 已完成实验

- 模型对比：baseline 为 [Quark MXFP8](https://huggingface.co/amd/MiniMax-M3.1-Flash-Quark-MXFP8)，对比模型为 [Quark MXFP4](https://huggingface.co/amd/MiniMax-M3.1-Flash-Quark-MXFP4)。两者均为量化 checkpoint；没有 BF16 原始模型结果。
- 运行框架：Pier 0.3.1 + mini-SWE-agent 2.4.5；版本和补丁指纹见 [versions.json](../data/versions.json)。
- 服务：vLLM 历史基础镜像 + 004 MXFP8 加载/推理支持，4 张 AMD GPU / TP4，512K 上下文，NVFP4 KV/indexer cache。
- 模型请求：Responses API，max_output_tokens=65536，reasoning_effort=max，temperature=1，top_p=0.95。
- 调度：每种模型三个顺序全量 job；每个 job 为113题、n-attempts=1、并发64、max-retries=2。
- 任务：固定 DeepSWE commit，独立 verifier；任务、提示词和评分没有本地修改。
- 任务 Docker daemon 独立，启用 init；agent 通过 Pier 白名单代理访问模型 API。
- MXFP8 第一次完整 job 使用 --delete，后两次使用 --no-delete；MXFP4 三次均为 --no-delete。中断的旧 MXFP8 第二次 job 不计入正式结果。

## 本仓库的新运行方式

根据最新要求，新脚本使用单个 `pier run --n-attempts 3`，113题各运行三次，共339个trial，共用并发64队列，统一 --no-delete。它不会按历史三次顺序 job 自动分成三个时间段。仍统计全部339次的平均通过率，不按每题取最佳答案。

部署也整理为独立的 Pier 控制镜像、模型服务镜像和沙箱 daemon。README 的最新得分来自已经完成的历史实验，不能宣称是在新 Compose 部署中重新测得。

## 仓库内可核对的数据

- [最新结果 JSON](../data/latest-results.json)：每个模型、每次历史 job 的通过数、耗时及逐题诊断。
- [678 个题目轮次 CSV](../data/trials.csv)：reward、退出/异常类型、截断数、工具超时数、token统计和原生result.json的SHA256。
- [版本指纹](../data/versions.json)：固定源码版本、基础镜像digest和补丁hash。
- [数据校验脚本](../scripts/check_published_data.py)：核对CSV/JSON的题数、通过数和诊断计数。

这些文件由完成的只读逐题审计导出，不包含完整模型轨迹、隐藏测试、参考解法或凭据。SHA256用于辨识来源文件，不代表公开了原始文件本身。要复现新结果，应按README建立自己的环境并保存自己的逐题产物。
