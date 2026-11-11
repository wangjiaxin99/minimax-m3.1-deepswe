# 仓库验证记录

验证日期：2026-11-11。平台为Linux x86_64，Docker Engine 28.3.2 / Compose 2.38.2。本仓库没有为验证重新运行339次模型评估；README中的分数来自已经完成的历史实验。

## 已验证

- 三个Dockerfile均实际构建成功：Pier控制器、vLLM补丁镜像、专用沙箱daemon。
- Pier从固定commit安装，并应用036/037；原生 `pier run --help` 可执行，支持脚本中的并发、attempt、重试及清理参数。
- vLLM镜像构建时004运行时补丁的目标SHA256与历史服务一致。没有启动新GPU模型服务。
- 固定DeepSWE commit获取成功，113份task.toml数量及工作树检查通过。
- 三个汇总测试通过：响应/工具调用去重、缺失reward保持分母、同题三个attempt按平均而非最佳计分。
- 公开678个题目轮次的JSON/CSV题数、通过数、截断和工具超时计数核对通过。新汇总脚本也只读重查了全部678份历史原生结果/轨迹，重新得到MXFP8 249/339、MXFP4 236/339，以及5/9次截断和637/583次工具超时。
- Bash/Python语法及Compose配置检查通过。
- 专用daemon可通过共享Unix socket连接，嵌套容器PID1使用docker-init。
- 443模型转发使用一个普通HTTP测试文件验证，不调用真实模型。
- 嵌套Docker DNS通过外层解析器转发验证成功；避免回退到机器无法访问的公共DNS。

## 网络策略检查

[check_sandbox.py](../scripts/check_sandbox.py)使用Pier原生网络生成代码建立合成容器，实际检查通过：本地模型地址代理请求成功；非白名单公共域名返回403；绕过代理的直接出口失败；容器PID1为docker-init。它不是DeepSWE任务，不生成模型答案或评估分数。测试容器及网络在检查后删除。

## 验证边界

历史全量实验已验证模型服务、mini-SWE和verifier的实际运行；新Dockerfile的构建与基础设施检查不等同于在新Compose部署中再次测得同样分数。

新运行方式按最新要求为一个job的`--n-attempts 3`，共339个trial；历史为三个顺序job、每job的attempt=1。新方式的端到端耗时尚未测量。模型远端revision、agent传递依赖、系统包、缓存和硬件差异应随新run记录。
