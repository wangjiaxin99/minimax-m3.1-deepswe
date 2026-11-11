# Third-party notices

This repository contains documentation, orchestration examples and read-only result metadata.

- `patches/001-vllm-quark-mxfp8.patch` is an archived diff from [vLLM PR #63125](https://github.com/vllm-project/vllm/pull/63125). vLLM is licensed under Apache-2.0; upstream authors retain their copyrights. The runtime application is limited to `quark_moe.py`.
- `patches/002-pier-provider-subnets.patch` and `patches/003-pier-mini-provider-allowlist.patch` are local modifications to [Datacurve Pier](https://github.com/datacurve-ai/pier), licensed under Apache-2.0. The patched upstream source is fetched during the Docker build.
- [DeepSWE](https://github.com/datacurve-ai/deep-swe) is downloaded at a pinned commit, not vendored into this repository. Its task code, embedded third-party repositories and reference solutions retain their own license and provenance requirements.
- Docker images, MiniMax models and Quark checkpoints retain their own licenses. This repository's Apache-2.0 license does not grant additional rights to those materials.
- Published trial metadata is a compact export of the author's local evaluation. It excludes full agent outputs, task solutions and model weights.
