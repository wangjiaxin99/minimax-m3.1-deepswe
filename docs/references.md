# 参考来源

- [DeepSWE](https://github.com/datacurve-ai/deep-swe/tree/0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea)：任务、资源、agent/verifier预算和独立verifier配置。官方README提供Pier + mini-SWE运行示例。
- [Pier](https://github.com/datacurve-ai/pier/tree/b26211ed2bbee6d145f6b8c5b80e39f18b296f08)：任务调度、agent安装、网络白名单、结果和轨迹收集。
- [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)：多轮代码修改、工具执行及模型调用。
- [Harbor任务格式](https://www.harborframework.com/docs/tasks#verifier-environment-shared-vs-separate)：任务配置及独立verifier格式。
- [vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125)：001补丁的MXFP8模型加载/推理支持。

本仓库的运行参数见 [README](../README.md)，版本指纹见 [versions.json](../data/versions.json)。
