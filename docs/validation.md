# 验证记录

2026-11-11完成以下检查：

- 三个Dockerfile实际构建成功。
- Pier原生CLI和固定113题源码检查通过。
- vLLM补丁后的源码SHA256与目标值一致。
- 汇总脚本测试通过，覆盖去重、缺失reward和每题三个attempt的平均计分。
- 678份原生结果/轨迹复核与公开CSV/JSON一致：MXFP8 249/339，MXFP4 236/339。
- Bash/Python语法、Compose配置和GitHub Actions检查通过。
- 专用Docker socket、DNS转发、HTTP转发及docker-init检查通过。
- 合成任务网络检查通过：白名单模型地址可达、公共域名返回403、直接出口被阻断。

基础设施检查未启动新的全量模型评估。
